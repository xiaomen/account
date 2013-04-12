#!/usr/local/bin/python2.7
#coding:utf-8

from flask.views import MethodView
from flaskext.csrf import csrf_exempt
from flask import g, redirect, url_for, request

from sheep.api.cache import backend

from utils.ua import check_ua
from utils.account import login_required
from views.topic.tools import clean_cache
from query.topic import get_topic, get_topic_users, \
        make_reply

class CreateReply(MethodView):
    decorators = [csrf_exempt, check_ua, login_required(next='account.login')]
    def get(self, tid):
        return redirect(url_for('topic.view', tid=tid))

    def post(self, tid):
        tid = request.form.get('tid')
        content = request.form.get('content')
        topic = get_topic(tid)
        sender, receiver = get_topic_users(g.current_user.id, topic.id)
        if not topic or not sender or not receiver:
            return redirect(url_for('topic.index'))
        make_reply(sender, receiver, topic, content)
        #clean cache
        clean_cache(g.current_user.id, receiver.uid, topic.id)
        backend.delete('topic:user_topic:%d:%d' % (g.current_user.id, topic.id))
        backend.delete('topic:user_topic:%d:%d' % (receiver.uid, topic.id))
        return redirect(url_for('topic.view', tid=tid))

