#!/usr/local/bin/python2.7
#coding:utf-8

from flask.views import MethodView
from flask import g, session, request, redirect, \
        url_for

from utils.token import make_token
from utils.account import login_required
from utils.ua import check_ua, render_template

from query.account import clear_user_cache

class OauthBind(MethodView):
    decorators = [check_ua]
    def get(self):
        return render_template('account.bind.html')

    def post(self):
        oauth = session.pop('from_oauth', None)
        allow = 'allow' in request.form
        if g.current_user and oauth and allow:
            oauth.bind(g.session['user_id'])
        return redirect(url_for('index'))

class WeixinBind(MethodView):
    decorators = [check_ua, login_required('account.login', redirect='/account/setting')]
    def get(self):
        user = g.current_user
        key = None
        if not user.weixin:
            key = make_token(user.id)
        return render_template('account.weixin.html', key = key)

    def post(self):
        user = g.current_user
        user.remove_weixin()
        clear_user_cache(user)
        return redirect(url_for("account.weixin_bind"))

