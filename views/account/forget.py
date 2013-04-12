#!/usr/local/bin/python2.7
#coding:utf-8

import logging
from datetime import datetime

from flask.views import MethodView
from flask import redirect, request, url_for, \
        abort, g
from flask import render_template as origin_render

from sheep.api.cache import backend

import config
from utils import code
from utils.account import login_required, account_login
from utils.validators import check_email
from utils.token import create_token
from utils.ua import check_ua, render_template
from utils.mail import send_email
from utils.validators import check_password

from query.account import get_user_by_email, create_forget, \
        get_forget_by_stub, get_user, clear_user_cache

logger = logging.getLogger(__name__)

class Forget(MethodView):
    decorators = [check_ua, login_required(need=False)]
    def get(self):
        if request.form and 'cancel' in request.form:
            return redirect(url_for('index'))
        return render_template('account.forget.html')

    def post(self):
        if request.form and 'cancel' in request.form:
            return redirect(url_for('index'))
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

class Reset(MethodView):
    decorators = [check_ua]
    def get(self, stub):
        forget = get_forget_by_stub(stub=stub)
        if g.current_user:
            if forget:
                forget.delete()
            return redirect(url_for('index'))

        if not forget:
            raise abort(404)

        if (datetime.now()  - forget.created).seconds > config.FORGET_STUB_EXPIRE:
            forget.delete()
            return render_template('account.reset.html', hidden=1, \
                    error=code.ACCOUNT_FORGET_STUB_EXPIRED)
        return render_template('account.reset.html', stub=stub)

    def post(self, stub):
        forget = get_forget_by_stub(stub=stub)
        if g.current_user:
            if forget:
                forget.delete()
            return redirect(url_for('index'))

        if not forget:
            raise abort(404)

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

