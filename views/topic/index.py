#!/usr/local/bin/python2.7
#coding:utf-8

from flask.views import MethodView
from flask import request, abort, g

from sheep.api.cache import backend

from utils.ua import render_template
from utils.account import login_required
from query.topic import get_user_topics
from views.topic.tools import format_topic_list

class Index(MethodView):
    decorators = [login_required(next='account.login')]

    def get(self):
        page = request.args.get('p', '1')
        if not page.isdigit():
            raise abort(404)
        page = int(page)
        msg = request.args.get('msg', None)
        list_page = get_user_topics(g.current_user.id, page)
        if page >1:
            page_1 = get_user_topics(g.current_user.id, 1)
            if list_page.total != page_1 or list_page.last_time != page_1.last_time:
                backend.delete('topic:list:%d:%d' % (g.current_user.id, page))
                list_page = get_user_topics(g.current_user.id, page)
        return render_template('topic.index.html', msg=msg, \
                topics=format_topic_list(list_page.items), list_page=list_page)

