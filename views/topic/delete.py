#!/usr/local/bin/python2.7
#coding:utf-8

from flask.views import MethodView
from flask import g, redirect, url_for

from sheep.api.cache import backend

from utils.ua import check_ua
from utils.account import login_required
from query.topic import get_user_topic, delete_topic

class Delete(MethodView):
    decorators = [check_ua, login_required(next='account.login')]
    def get(self, tid):
        user_topic = get_user_topic(g.current_user.id, tid=tid)
        if user_topic:
            delete_topic(user_topic)
            backend.delete('topic:meta:%d' % g.current_user.id)
            backend.delete('topic:list:%d:1' % g.current_user.id)
            backend.delete('topic:user_topic:%d:%d' % (g.current_user.id, tid))
        return redirect(url_for('topic.index'))

