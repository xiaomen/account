#!/usr/local/bin/python2.7
#coding:utf-8

import json
import config
import logging
from utils import *
from datetime import datetime
from sheep.api.cache import backend
from models.account import db, User, Forget, create_token
from flask import Blueprint, g, session, jsonify, \
        redirect, request, url_for, render_template, \
        abort
from flaskext.csrf import csrf_exempt

logger = logging.getLogger(__name__)

account = Blueprint('account', __name__)

@account.route('/forget', methods=['GET', 'POST'])
def forget():
    if get_current_user() or \
            (request.form and 'cancel' in request.form):
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('forget.html')
    email = request.form.get('email', None)
    status = check_email(email)
    if status:
        return render_template('forget.html', error=status[1])
    user = get_user_by_email(email=email)
    if user:
        stub = create_token(20)
        try:
            send_email(user.email, \
                'Xiaomen.co Account Service',
                r'''http://account.xiaomen.co/account/reset/%s click this''' % stub)
        except:
            logger.exception("send mail failed")

        db.session.add(Forget(user.id, stub))
        db.session.commit()

    return render_template('forget.html', send=1)

@account.route('/reset/<stub>', methods=['GET', 'POST'])
def reset(stub=None):
    forget = get_forget_by_stub(stub=stub)
    if get_current_user():
        if forget:
            _delete_forget(forget)
            db.session.commit()
        return redirect(url_for('index'))

    if not forget:
        raise abort(404)

    if request.method == 'GET':
        if (datetime.now()  - forget.created).total_seconds() > config.FORGET_STUB_EXPIRE:
            _delete_forget(forget)
            db.session.commit()
            return render_template('reset.html', hidden=1, \
                    error='stub expired')
        return render_template('reset.html', stub=stub)

    password = request.form.get('password', None)
    status = check_password(password)
    if status:
        return render_template('reset.html', stub=stub, \
                error=status[1])
    user = get_user(forget.uid)
    _change_password(user, password)
    backend.delete('account:%s' % forget.stub)
    _delete_forget(forget)
    db.session.commit()
    clear_user_cache(user)
    return render_template('reset.html', ok=1)

@account.route('/bind', methods=['GET', 'POST'])
def bind():
    if request.method == 'GET':
        return render_template('bind.html')
    oauth = session.pop('from_oauth', None)
    allow = 'allow' in request.form
    user = get_current_user()
    if user and oauth and allow:
        _bind_oauth(oauth, g.session['user_id'])
    return redirect(url_for('index'))

@account.route('/register', methods=['POST','GET'])
def register():
    if get_current_user():
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('register.html')
    username = request.form.get('name', None)
    password = request.form.get('password', None)
    email = request.form.get('email', None)
    check, error = check_register_info(username, email, password)
    if not check:
        return render_template('register.html', error=error)
    oauth = session.pop('from_oauth', None)
    user = User(username, password, email)
    db.session.add(user)
    db.session.commit()
    #clear cache
    clear_user_cache(user)
    account_login(user)
    if oauth:
        _bind_oauth(oauth, user.id)
    return redirect(url_for('index'))

@csrf_exempt
@account.route('/login', methods=['POST', 'GET'])
def login():
    if get_current_user():
        return redirect(url_for('index'))
    login_url = url_for('account.login', **request.args)
    if request.method == 'GET':
        return render_template('index.html', login_url=login_url)
    password = request.form.get('password', None)
    email = request.form.get('email', None)
    check, error = check_login_info(email, password)
    if not check:
        return render_template('index.html', login_info=error, login_url=login_url)

    user = get_user_by_email(email=email)
    if not user:
        logger.info('no such user')
        return render_template('index.html', login_info='no such user', login_url=login_url)
    if not user.check_password(password):
        logger.info('invaild passwd')
        return render_template('index.html', login_info='invaild passwd', login_url=login_url)

    account_login(user)
    redirect_url = request.args.get('redirect', None)
    return redirect(redirect_url or url_for('index'))

@account.route('/logout')
def logout():
    account_logout()
    return redirect(request.referrer or url_for('index'))

@account.route('/setting', methods=['POST', 'GET'])
def setting():
    user = get_current_user()
    if not user:
        return redirect(url_for('account.login'))

    if request.method == 'GET':
        return render_template('setting.html', \
                user=user)
    username = request.form.get('name', None)
    password = request.form.get('password', None)
    domain = request.form.get('domain', None)

    if username != user.name:
        status = check_username(username)
        if status:
            return render_template('setting.html', error=status[1], user=user)
        _change_username(user, username)

    if domain:
        for status in [check_domain(domain), check_domain_exists(domain)]:
            if status:
                return render_template('setting.html', error=status[1], user=user)
        _set_domain(user, domain)

    if password:
        status = check_password(password)
        if status:
            return render_template('setting.html', error=status[1], user=user)
        _change_password(user, password)
    db.session.commit()
    #clear cache
    clear_user_cache(user)
    return render_template('setting.html', error='update ok', user=user)

def clear_user_cache(user):
    keys = ['account:%s' % key for key in [str(user.id), user.domain, user.email]]
    backend.delete_many(*keys)

def _set_domain(user, domain):
    user.domain = domain
    db.session.add(user)

def _delete_forget(forget):
    db.session.delete(forget)

def _change_password(user, password):
    user.token = create_token(16)
    user.passwd = User.create_password(password)
    account_login(user)
    db.session.add(user)

def _change_username(user, username):
    user.name = username
    db.session.add(user)

def _bind_oauth(oauth, uid):
    oauth.bind(uid)
    db.session.add(oauth)
    db.session.commit()

def account_login(user):
    g.session['user_id'] = user.id
    g.session['user_token'] = user.token

def account_logout():
    g.session.clear()

