#!/usr/local/bin/python2.7
#coding:utf-8

import logging
from utils import *
from flask import g, request, url_for, \
        render_template, abort, Blueprint

logger = logging.getLogger(__name__)

people = Blueprint('people', __name__)

@people.route('/<username>')
def show_people(username):
    current_user = get_current_user()
    visit_user = get_user(username)
    if not visit_user:
        raise abort(404)
    return render_template('people.html', \
            current_user = current_user, \
            visit_user = visit_user, \
            setting_url = url_for('account.setting'))

