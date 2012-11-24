#!/usr/local/bin/python2.7
#coding:utf-8

import config
import logging
import tempfile
from utils import *
from datetime import datetime
from sheep.api.files import get_uploader
from sheep.api.cache import backend, cross_cache
from models.account import db, User, Forget, create_token
from flask import Blueprint, g, session, \
        redirect, request, url_for, abort
from flask import render_template as origin_render
from flaskext.csrf import csrf_exempt

logger = logging.getLogger(__name__)

account = Blueprint('account', __name__)

@csrf_exempt
@account.route('/forget', methods=['GET', 'POST'])
@check_ua
@login_required(need=False)
def forget():
    if request.form and 'cancel' in request.form:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('account.forget.html')
    email = request.form.get('email', None)
    status = check_email(email)
    if status:
        return render_template('account.forget.html', error=status[1])
    user = get_user_by_email(email=email)
    if user:
        stub = create_token(20)
        try:
            send_email(user.email, \
                config.FORGET_EMAIL_TITLE,
                origin_render('email.html', user=user, stub=stub))
        except:
            logger.exception("send mail failed")

        db.session.add(Forget(user.id, stub))
        db.session.commit()

    return render_template('account.forget.html', send=1)

@account.route('/reset/<stub>', methods=['GET', 'POST'])
@check_ua
def reset(stub=None):
    forget = get_forget_by_stub(stub=stub)
    if g.current_user:
        if forget:
            _delete_forget(forget)
            db.session.commit()
        return redirect(url_for('index'))

    if not forget:
        raise abort(404)

    if request.method == 'GET':
        if (datetime.now()  - forget.created).seconds > config.FORGET_STUB_EXPIRE:
            _delete_forget(forget)
            db.session.commit()
            return render_template('account.reset.html', hidden=1, \
                    error='stub expired')
        return render_template('account.reset.html', stub=stub)

    password = request.form.get('password', None)
    status = check_password(password)
    if status:
        return render_template('account.reset.html', stub=stub, \
                error=status[1])
    user = get_user(forget.uid)
    _change_password(user, password)
    backend.delete('account:%s' % forget.stub)
    _delete_forget(forget)
    db.session.commit()
    clear_user_cache(user)
    return render_template('account.reset.html', ok=1)

@account.route('/bind', methods=['GET', 'POST'])
@check_ua
def bind():
    if request.method == 'GET':
        return render_template('account.bind.html')
    oauth = session.pop('from_oauth', None)
    allow = 'allow' in request.form
    if g.current_user and oauth and allow:
        _bind_oauth(oauth, g.session['user_id'])
    return redirect(url_for('index'))

@csrf_exempt
@account.route('/register', methods=['POST','GET'])
@check_ua
@login_required(need=False)
def register():
    if request.method == 'GET':
        return render_template('account.register.html')
    username = request.form.get('name', None)
    password = request.form.get('password', None)
    email = request.form.get('email', None)
    check, error = check_register_info(username, email, password)
    if not check:
        return render_template('account.register.html', error=error)
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
@check_ua
@login_required(need=False)
def login():
    login_url = url_for('account.login', **request.args)
    if request.method == 'GET':
        return render_template('account.login.html', login_url=login_url)
    password = request.form.get('password', None)
    email = request.form.get('email', None)
    check, error = check_login_info(email, password)
    if not check:
        return render_template('account.login.html', login_info=error, login_url=login_url)

    user = get_user_by_email(email=email)
    if not user:
        logger.info('no such user')
        return render_template('account.login.html', login_info='no such user', login_url=login_url)
    if not user.check_password(password):
        logger.info('invaild passwd')
        return render_template('account.login.html', login_info='invaild passwd', login_url=login_url)

    account_login(user)
    redirect_url = request.args.get('redirect', None)
    return redirect(redirect_url or url_for('index'))

@csrf_exempt
@account.route('/logout')
@check_ua
def logout():
    account_logout()
    return redirect(request.referrer or url_for('index'))

@account.route('/avatar', methods=['POST', 'GET'])
@check_ua
@login_required('account.login', redirect='/account/avatar')
def avatar():
    user = g.current_user
    if request.method == 'GET':
        return render_template('account.avatar.html', path='/'+user.avatar)
    upload_avatar = request.files['file']
    if not upload_avatar or not allowed_file(upload_avatar.filename):
        #TODO use template
        return 'error'
    uploader = get_uploader()
    filename, stream, error = process_file(user, upload_avatar)
    if error:
        #TODO use template
        return 'error'
    uploader.writeFile(filename, stream)
    _set_avatar(user, filename)
    clear_user_cache(user)
    return 'OK'

@account.route('/setting', methods=['POST', 'GET'])
@check_ua
@login_required('account.login', redirect='/account/setting')
def setting():
    user = g.current_user
    if request.method == 'GET':
        return render_template('account.setting.html')

    username = request.form.get('name', None)
    password = request.form.get('password', None)
    domain = request.form.get('domain', None)

    if username != user.name:
        status = check_username(username)
        if status:
            return render_template('account.setting.html', error=status[1])
        _change_username(user, username)

    if domain:
        for status in [check_domain(domain), check_domain_exists(domain)]:
            if status:
                return render_template('account.setting.html', error=status[1])
        _set_domain(user, domain)

    if password:
        status = check_password(password)
        if status:
            return render_template('account.setting.html', error=status[1])
        _change_password(user, password)
    db.session.commit()
    #clear cache
    clear_user_cache(user)
    g.current_user = get_current_user()
    return render_template('account.setting.html', error='update ok')

def clear_user_cache(user):
    keys = ['account:%s' % key for key in [str(user.id), user.domain, user.email]]
    backend.delete_many(*keys)
    cross_cache.delete('open:account:info:{0}'.format(user.id))

def _set_avatar(user, filename):
    user.avatar = filename
    db.session.add(user)
    db.session.commit()

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

