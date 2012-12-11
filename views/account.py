#!/usr/local/bin/python2.7
#coding:utf-8

import config
import logging
from datetime import datetime

from utils import code
from utils.ua import check_ua, render_template
from utils.account import login_required, process_file
from utils.validators import check_email, check_password, \
        check_register_info, check_login_info, check_domain, \
        check_domain_exists, check_username
from utils.mail import send_email
from query.account import get_user_by_email, get_user, \
        get_forget_by_stub, get_current_user, create_forget, \
        create_user

from sheep.api.files import get_uploader
from sheep.api.cache import backend, cross_cache
from models.account import create_token

from flask import Blueprint, g, session, \
        redirect, request, url_for, abort
from flask import render_template as origin_render
from flaskext.csrf import csrf_exempt

logger = logging.getLogger(__name__)

account = Blueprint('account', __name__)

@csrf_exempt
@account.route('/forget/', methods=['GET', 'POST'])
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
        create_forget(user.id, stub)
    return render_template('account.forget.html', send=1)

@account.route('/reset/<stub>/', methods=['GET', 'POST'])
@check_ua
def reset(stub=None):
    forget = get_forget_by_stub(stub=stub)
    if g.current_user:
        if forget:
            forget.delete()
        return redirect(url_for('index'))

    if not forget:
        raise abort(404)

    if request.method == 'GET':
        if (datetime.now()  - forget.created).seconds > config.FORGET_STUB_EXPIRE:
            forget.delete()
            return render_template('account.reset.html', hidden=1, \
                    error=code.ACCOUNT_FORGET_STUB_EXPIRED)
        return render_template('account.reset.html', stub=stub)

    password = request.form.get('password', None)
    status = check_password(password)
    if status:
        return render_template('account.reset.html', stub=stub, \
                error=status[1])
    user = get_user(forget.uid)
    user.change_password(password)
    account_login(user)
    forget.delete()
    clear_user_cache(user)
    backend.delete('account:%s' % forget.stub)
    return render_template('account.reset.html', ok=1)

@account.route('/bind', methods=['GET', 'POST'])
@check_ua
def bind():
    if request.method == 'GET':
        return render_template('account.bind.html')
    oauth = session.pop('from_oauth', None)
    allow = 'allow' in request.form
    if g.current_user and oauth and allow:
        oauth.bind(g.session['user_id'])
    return redirect(url_for('index'))

@csrf_exempt
@account.route('/register/', methods=['POST','GET'])
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
    user = create_user(username, password, email)
    #clear cache
    clear_user_cache(user)
    account_login(user)
    if oauth:
        oauth.bind(user.id)
    return redirect(url_for('index'))

@csrf_exempt
@account.route('/login/', methods=['POST', 'GET'])
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
@account.route('/logout/')
@check_ua
def logout():
    account_logout()
    return redirect(request.referrer or url_for('index'))

@account.route('/avatar/', methods=['POST', 'GET'])
@check_ua
@login_required('account.login', redirect='/account/avatar/')
def avatar():
    user = g.current_user
    if request.method == 'GET':
        ok = request.args.get('ok', None)
        return render_template('account.avatar.html', path = user.avatar, ok=ok)
    upload_avatar = request.files['file']
    if not upload_avatar:
        return render_template('account.avatar.html', path = user.avatar, error = 'Please select avatar file')
    uploader = get_uploader()
    filename, stream, error = process_file(user, upload_avatar)
    if error:
        return render_template('account.avatar.html', path = user.avatar, error = error)
    uploader.writeFile(filename, stream)
    user.set_avatar(filename)
    clear_user_cache(user)
    return redirect(url_for('account.avatar', ok = 1))

@account.route('/setting/', methods=['POST', 'GET'])
@check_ua
@login_required('account.login', redirect='/account/setting/')
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
        user.change_username(username)

    if domain:
        for status in [check_domain(domain), check_domain_exists(domain)]:
            if status:
                return render_template('account.setting.html', error=status[1])
        user.set_domain(domain)

    if password:
        status = check_password(password)
        if status:
            return render_template('account.setting.html', error=status[1])
        user.change_password(password)
    #clear cache
    clear_user_cache(user)
    account_login(user)
    g.current_user = get_current_user()
    return render_template('account.setting.html', error=code.ACCOUNT_SETTING_SUCCESS)

def clear_user_cache(user):
    keys = ['account:%s' % key for key in [str(user.id), user.domain, user.email]]
    backend.delete_many(*keys)
    cross_cache.delete('open:account:info:{0}'.format(user.id))

def account_login(user):
    g.session['user_id'] = user.id
    g.session['user_token'] = user.token

def account_logout():
    g.session.clear()

