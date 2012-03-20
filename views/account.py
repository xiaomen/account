#!/usr/local/bin/python2.7
#coding:utf-8

import re
import json
import logging
from models import db, User, Domain
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
    if g.user and oauth and allow:
        bind_oauth(oauth, g.session['user_id'])
    return redirect(url_for('index'))

@account.route('/register', methods=['POST','GET'])
def register():
    if g.user:
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
    if g.user:
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
    if not g.user:
        return redirect(url_for('account.login'))
    user = User.query.get(g.session['user_id'])
    if request.method == 'GET':
        return render_template('setting.html')
    username = request.form.get('name', None)
    password = request.form.get('password', None)
    domain = request.form.get('domain', None)



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

def check_register_info(username, email, password):
    '''
    username a-zA-Z0-9_-, >4 <20
    email a-zA-Z0-9_-@a-zA-Z0-9.a-zA-Z0-9
    password a-zA-Z0-9_-!@#$%^&*
    '''
    if not (username and email and password):
        return False, 'value is empty'
    if not re.search(r'^[a-zA-Z]{3,20}$', username, re.I):
        return False, 'username invail'
    if not re.search(r'^.+@[^.].*\.[a-z]{2,10}$', email, re.I):
        return False, 'email invaild'
    user = User.query.filter_by(email=email).first()
    if user:
        return False, 'email exists'
    if not re.search(r'[\S]{6,}', password, re.I):
        return False, 'password invaild'
    return True, None

def check_login_info(email, password):
    if not password:
        return False, 'need password'
    if not email or not re.search(r'\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*', email, re.I):
        return False, 'email invaild'
    return True, None
