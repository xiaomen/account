#!/usr/bin/python
# encoding: UTF-8

import config
import logging
from models import *
from lib.weibo import weibo, GET
from sheep.api.statics import static_files
from flask import Flask, render_template, redirect, \
    request, session, url_for, g

app = Flask(__name__)
app.debug = config.DEBUG
app.secret_key = config.SECRET_KEY
app.jinja_env.filters['s_files'] = static_files

init_db()

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    if g.user is None:
        return render_template('index.html')
    else:
        logout = '<a href="/Logout">Logout</a>'
        user_info = GET("/users/show/", g.user.uid)
        logger.info(user_info.data)
        return render_template('index.html', logout=logout)

@app.route('/Logout')
def logout():
    session.pop('user_id', None)
    return redirect(request.referrer or url_for('index'))

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.filter_by(uid=session['user_id']).first()

@app.after_request
def after_request(response):
    db_session.remove()
    return response

from views.weibo import *
app.add_url_rule('/Login/Weibo', view_func=weibo_login)
app.add_url_rule('/Authorized/Weibo', view_func=weibo_authorized)
