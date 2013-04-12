#!/usr/local/bin/python2.7
#coding:utf-8

import logging
from flask import abort
from flask.views import MethodView

from query.account import get_user
from utils.ua import render_template

logger = logging.getLogger(__name__)

class People(MethodView):
    def get(self, username):
        visit_user = get_user(username)
        if not visit_user:
            raise abort(404)
        return render_template('account.people.html', \
                visit_user = visit_user)

