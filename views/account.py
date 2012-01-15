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

@account.route('/Register', methods=['POST','GET'])
def register():
    if g.user is not None:
        #TODO 已注册用户如果没oauth直接到account首页
        # 有oauth type信息则提示添加账号
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

    password = make_passwd(email, password)
    user = User(username, password, email)
    db_session.add(user)
    db_session.commit()
    if oauth:
        oauth.uid = user.id
        db_session.add(oauth)
        db_session.commit()
    session['user_id'] = user.id
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

