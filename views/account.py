#!/usr/local/bin/python2.7
#coding:utf-8

import re
import json
import logging
from utils import get_current_user
from models import db, User, Profile, create_token
from flask import Blueprint, g, session, jsonify, \
        redirect, request, url_for, render_template
from flaskext.csrf import csrf_exempt

logger = logging.getLogger(__name__)

account = Blueprint('account', __name__)

@account.route('/bind', methods=['GET', 'POST'])
def bind():
    if request.method == 'GET':
        return render_template('bind.html')
    oauth = session.pop('from_oauth', None)
    allow = 'allow' in request.form
    user = get_current_user()
    if user and oauth and allow:
        bind_oauth(oauth, g.session['user_id'])
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
    _login(user)
    if oauth:
        bind_oauth(oauth, user.id)
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

    user = User.query.filter_by(email=email).first()
    if not user:
        logger.info('no such user')
        return render_template('index.html', login_info='no such user', login_url=login_url)
    if not user.check_password(password):
        logger.info('invaild passwd')
        return render_template('index.html', login_info='invaild passwd', login_url=login_url)

    _login(user)
    redirect_url = request.args.get('redirect', None)
    return redirect(redirect_url or url_for('index'))

@account.route('/logout')
def logout():
    _logout()
    return redirect(request.referrer or url_for('index'))

@account.route('/setting', methods=['POST', 'GET'])
def setting():
    user = get_current_user()
    if not user:
        return redirect(url_for('account.login'))
    profile = Profile.query.filter_by(uid=g.session['user_id']).first()
    if not profile:
        profile = Profile(user.id)

    if request.method == 'GET':
        return render_template('setting.html', \
                user=user, profile=profile)
    username = request.form.get('name', None)
    password = request.form.get('password', None)
    domain = request.form.get('domain', None)

    if username != user.name:
        check, error = check_update_info(username)
        if not check:
            return render_template('setting.html', error=error, user=user)
    _change_username(user, username)

    if password:
        status = _check_password(password)
        if status:
            return render_template('setting.html', error=status[0], user=user)
        _change_password(user, password)

    if domain:
        status = _check_domain(domain)
        if status:
            return render_template('setting.html', error=status[0], user=user)
        _set_domain(profile, user, domain)
    db.session.commit()
    return render_template('setting.html', error='update ok', \
            profile=profile, user=user)

def _set_domain(profile, user, domain):
    profile.domain = domain
    db.session.add(profile)

def _change_password(user, password):
    user.token = create_token(16)
    user.password = User.create_password(password)
    db.session.add(user)

def _change_username(user, username):
    user.name = username
    db.session.add(user)

def _login(user):
    g.session['user_id'] = user.id
    g.session['user_token'] = user.token

def _logout():
    g.session.pop('user_id', None)
    g.session.pop('user_token', None)

def bind_oauth(oauth, uid):
    oauth.bind(uid)
    db.session.add(oauth)
    db.session.commit()

def check_update_info(username):
    status = _check_username(username),
    if status:
        return status
    return True, None

def check_register_info(username, email, password):
    '''
    username a-zA-Z0-9_-, >4 <20
    email a-zA-Z0-9_-@a-zA-Z0-9.a-zA-Z0-9
    password a-zA-Z0-9_-!@#$%^&*
    '''
    check_list = [
        _check_username(username),
        _check_email(email),
        _check_email_exists(email),
        _check_password(password),
    ]
    for status in check_list:
        if not status:
            continue
        return status
    return True, None

def check_login_info(email, password):
    check_list = [
        _check_password(password),
        _check_email(email),
    ]
    for status in check_list:
        if not status:
            continue
        return status
    return True, None

def _check_password(password):
    if not password:
        return False, 'need password'
    if not re.search(r'[\S]{6,}', password, re.I):
        return False, 'password invaild'

def _check_domain(domain):
    if not domain:
        return False, 'need domain'
    if not re.search(r'^[a-zA-Z0-9_-]{4,10}$', domain, re.I):
        return False, 'domain invail'

def _check_username(username):
    if not username:
        return False, 'need username'
    if not re.search(r'^[a-zA-Z0-9_-]{3,20}$', username, re.I):
        return False, 'username invail'

def _check_email(email):
    if not email:
        return False, 'need email'
    if not re.search(r'^.+@[^.].*\.[a-z]{2,10}$', email, re.I):
        return False, 'email invaild'

def _check_email_exists(email):
    if not email:
        return False, 'need email'
    user = User.query.filter_by(email=email).first()
    if user:
        return False, 'email exists'

