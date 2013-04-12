#!/usr/local/bin/python2.7
#coding:utf-8

from flask.views import MethodView
from flask import g, redirect, url_for, request, \
        abort

from query.topic import make_topic

from query.account import get_user
from views.topic.tools import clean_cache
from utils.account import login_required
from utils.ua import check_ua, render_template

class CreateTopic(MethodView):
    decorators = [check_ua, login_required(next='account.login')]
    def get(self, uid):
        if uid == g.current_user.id:
            return redirect(url_for('topic.index'))
        who = get_user(uid)
        if not who:
            raise abort(404)
        return render_template('topic.create.html', uid=uid, who=who)

    def post(self, uid):
        if uid == g.current_user.id:
            return redirect(url_for('topic.index'))
        who = get_user(uid)
        to_uid = request.form.get('to_uid')
        title = request.form.get('title')
        content = request.form.get('content')
        if not who:
            #TODO return error code
            # check other params
            return render_template('topic.create.html', uid=uid)
        topic = make_topic(g.current_user.id, to_uid, title, content)
        #clean cache
        clean_cache(g.current_user.id, uid, topic.id)
        return redirect(url_for('topic.index'))

