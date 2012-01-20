#!/usr/local/bin/python2.7
#coding:utf-8

import logging
import hashlib
from models import *
from utils import bind_oauth
from flask import Blueprint, session, g, \
        redirect, request, url_for, render_template

logger = logging.getLogger(__name__)

account = Blueprint('account', __name__)

@account.route('/')
def index():
    if g.user is None:
        return render_template('account.html')
    return render_template('logout.html')

@account.route('/Bind', methods=['GET', 'POST'])
def bind():
    if request.method == 'GET':
        return render_template('bind.html')
    oauth = session.pop('from_oauth', None)
    allow = 'allow' in request.form
    if g.user and oauth and allow:
        bind_oauth(oauth, g.user.id)
    return redirect(url_for('index'))

@account.route('/Register', methods=['POST','GET'])
def register():
    if g.user is not None:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('register.html')
    oauth = session.pop('from_oauth', None)
    username = request.form.get('name', None)
    password = request.form.get('password', None)
    email = request.form.get('email', None)
    #TODO escape 参数
    if not (username and password and email):
        return render_template('register.html')
    user = User(username, password, email)
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id
    if oauth:
        bind_oauth(oauth, user.id)
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

    user = User.query.filter_by(email=email).first()
    if not user:
        logger.info('no such user')
        return render_template('login.html', info='no such user')
    if not user.check_password(password):
        logger.info('invaild passwd')
        return render_template('login.html', info='invaild passwd')

    session['user_id'] = user.id
    return redirect(url_for('index'))

@account.route('/Logout')
def logout():
    session.pop('user_id', None)
    session.pop('user', None)
    return redirect(request.referrer or url_for('index'))

