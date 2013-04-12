#!/usr/local/bin/python2.7
#coding:utf-8

from flask.views import MethodView
from flask import g, request, abort

from sheep.api.cache import backend

from utils.ua import render_template
from utils.account import login_required
from query.topic import get_topic, get_user_replies, \
        mark_read
from views.topic.tools import format_reply_list

class View(MethodView):
    decorators = [login_required(next='account.login')]
    def get(self, tid):
        page = request.args.get('p', '1')
        topic = get_topic(tid)
        if not topic or not page.isdigit():
            raise abort(404)
        page = int(page)
        if mark_read(g.current_user.id, tid):
            backend.delete('topic:user_topic:%d:%d' % (g.current_user.id, tid))
            backend.delete('topic:notify:%d' % g.current_user.id)
            backend.delete('topic:list:%d:1' % g.current_user.id)
        list_page = get_user_replies(tid, page)
        if page > 1 and list_page.total != get_user_replies(tid, 1):
            backend.delete('topic:replies:%d:%d' % (tid, page))
            list_page = get_user_replies(tid, page)
        #TODO check reply count!!!
        return render_template('topic.view.html', \
                replies=format_reply_list(list_page.items), \
                topic=topic, list_page=list_page)
