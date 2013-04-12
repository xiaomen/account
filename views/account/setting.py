#!/usr/local/bin/python2.7
#coding:utf-8

import time

from flask import g, request, \
        redirect, url_for
from flask.views import MethodView

from sheep.api.files import get_uploader, purge

from utils import code
from utils.ua import check_ua, render_template
from utils.account import login_required, account_login, \
        process_file
from utils.validators import check_password, check_domain, \
        check_domain_exists, check_username

from query.account import clear_user_cache, get_current_user

class Setting(MethodView):
    decorators = [check_ua, login_required('account.login', redirect='/account/setting/')]
    def get(self):
        return render_template('account.setting.html')

    def post(self):
        user = g.current_user
        username = request.form.get('name', None)
        password = request.form.get('password', None)
        domain = request.form.get('domain', None)

        if username != user.name:
            status = check_username(username)
            if status:
                return render_template('account.setting.html', error=status[1])
            user.change_username(username)

        if domain and not user.domain:
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

class Avatar(MethodView):
    decorators = [check_ua, login_required('account.login', redirect='/account/avatar/')]
    def get(self):
        user = g.current_user
        ok = request.args.get('ok', None)
        return render_template('account.avatar.html', path = user.avatar, ok = ok, \
                salt = time.time())

    def post(self):
        user = g.current_user
        upload_avatar = request.files['file']
        if not upload_avatar:
            return render_template('account.avatar.html', path = user.avatar, error = 'Please select avatar file')
        uploader = get_uploader()
        filename, stream, error = process_file(user, upload_avatar)
        if error:
            return render_template('account.avatar.html', path = user.avatar, error = error)
        uploader.writeFile(filename, stream)
        purge(filename)
        user.set_avatar(filename)
        clear_user_cache(user)
        return redirect(url_for('account.avatar', ok = 1))

