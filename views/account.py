#!/usr/local/bin/python2.7
#coding:utf-8

import logging
import hashlib
from models import *
from flask import Blueprint, session, g, \
        redirect, request, url_for, render_template

logger = logging.getLogger(__name__)

account = Blueprint('account', __name__)

@account.route('/')
def index():
    if g.user is None:
        return render_template('account.html')
    return render_template('logout.html')

@account.route('/Bind', methods=['POST'])
def bind():
    oauth = session.pop('from_oauth', None)
    allow = 'allow' in request.form
    if g.user and oauth and allow:
        bind(oauth, g.user.id)
    return redirect(request.referrer or url_for('index'))

@account.route('/Register', methods=['POST','GET'])
def register():
    oauth = session.get('from_oauth', None)
    if g.user is not None:
        if oauth:
            return render_template('bind.html')
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('register.html')
    username = request.form.get('name', None)
    password = request.form.get('password', None)
    email = request.form.get('email', None)
    #TODO escape 参数
    if not (username and password and email):
        return render_template('register.html')
    password = make_passwd(email, password)
    user = User(username, password, email)
    db_session.add(user)
    db_session.commit()
    session['user_id'] = user.id
    if oauth:
        bind(oauth, user.id)
    return redirect(url_for('index'))

@account.route('/Login', methods=['POST', 'GET'])
def login():
    if g.user is not None:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('login.html')
    password = request.form.get('password', None)
    email = request.form.get('email', None)
    if not (password and email):
        return render_template('login.html', info='less info')

    password = make_passwd(email, password)
    user = User.query.filter_by(email=email,passwd=password).first()
    if not user:
        logger.info('invaild login')
        return render_template('Login.html', info='invaild')
    session['user_id'] = user.id
    return redirect(url_for('index'))

@account.route('/Logout')
def logout():
    session.pop('user_id', None)
    session.pop('user', None)
    return redirect(request.referrer or url_for('index'))

def make_passwd(username, password):
    m = hashlib.sha1()
    m.update(username)
    p1 = m.hexdigest()
    p1 = p1[10:20] + p1[:10]
    m = hashlib.md5()
    m.update(p1)
    m.update(password)
    return m.hexdigest()

def bind(oauth, uid):
    oauth.uid = uid
    db_session.add(oauth)
    db_session.commit()
