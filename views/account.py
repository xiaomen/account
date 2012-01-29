#!/usr/local/bin/python2.7
#coding:utf-8

import re
import urllib
import logging
from models import db, User
from flask import Blueprint, session, g, \
        redirect, request, url_for, render_template
from flaskext.csrf import csrf_exempt

logger = logging.getLogger(__name__)

account = Blueprint('account', __name__)

@account.route('/')
def index():
    if g.user is None:
        return render_template('index.html')
    return render_template('index.html', login=1)

@account.route('/bind', methods=['GET', 'POST'])
def bind():
    if request.method == 'GET':
        return render_template('bind.html')
    oauth = session.pop('from_oauth', None)
    allow = 'allow' in request.form
    if g.user and oauth and allow:
        bind_oauth(oauth, g.user.id)
    return redirect(url_for('index'))

@account.route('/register', methods=['POST','GET'])
def register():
    if g.user is not None:
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
    session['user_id'] = user.id
    if oauth:
        bind_oauth(oauth, user.id)
    return redirect(url_for('index'))

@csrf_exempt
@account.route('/login', methods=['POST', 'GET'])
def login():
    if g.user is not None:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('index.html')
    password = request.form.get('password', None)
    email = request.form.get('email', None)
    check, error = check_login_info(email, password)
    if not check:
        return render_template('index.html', login_info=error)

    user = User.query.filter_by(email=email).first()
    if not user:
        logger.info('no such user')
        return render_template('index.html', login_info='no such user')
    if not user.check_password(password):
        logger.info('invaild passwd')
        return render_template('index.html', login_info='invaild passwd')

    session['user_id'] = user.id
    return redirect(url_for('index'))

@account.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user', None)
    return redirect(request.referrer or url_for('index'))

@account.route('/sso')
def sso():
    callback_url = request.args.get('callback', '')
    redirect_url = request.args.get('redirect', '') or url_for('index')
    state = request.args.get('state', '')
    if not callback_url:
        return 'callback_url is missing'
    if not g.user:
        r = '-1'
    else:
        r = str(g.user.id)
        #return redirect(url_for('account.login', redirect=redirect_url, callback=callback_url, state=state))
    callback_url += '?state=%s&redirect=%s&r=%s' % (state, redirect_url, urllib.quote(r))
    return redirect(callback_url)

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
    if not re.search(r'^[a-zA-Z][\w-]{3,20}$', username, re.I):
        return False, 'username invail'
    if not re.search(r'\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*', email, re.I):
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
