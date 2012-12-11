#!/usr/local/bin/python2.7
#coding:utf-8

import logging
from query.account import get_user
from utils.ua import render_template
from flask import abort, Blueprint

logger = logging.getLogger(__name__)

people = Blueprint('people', __name__)

@people.route('/<username>/')
def show_people(username):
    visit_user = get_user(username)
    if not visit_user:
        raise abort(404)
    return render_template('account.people.html', \
            visit_user = visit_user)

