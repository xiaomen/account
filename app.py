#!/usr/bin/python
# encoding: UTF-8

import config
import logging
from models import *
from lib.weibo import weibo, GET
from views.weibo import weibo_oauth
from views.douban import douban_oauth
from views.account import account
from sheep.api.statics import static_files
from flask import Flask, render_template, session, g

app = Flask(__name__)
app.debug = config.DEBUG
app.secret_key = config.SECRET_KEY
app.jinja_env.filters['s_files'] = static_files
app.register_blueprint(weibo_oauth, url_prefix='/Weibo')
app.register_blueprint(douban_oauth, url_prefix='/Douban')
app.register_blueprint(account, url_prefix='/Account')

logger = logging.getLogger(__name__)

init_db()

@app.route('/')
def index():
    if g.user is None:
        return render_template('index.html')
    else:
        logout = '<a href="/Account/Logout">Logout</a>'
        oauth_info = g.oauth('weibo')
        values = {}
        if oauth_info:
            user_info = GET("/users/show/", oauth_info.oauth_uid)
            if user_info.status == 200:
                values = user_info.data
        return render_template('index.html', logout=logout, values=values)

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session and session['user_id']:
        if not session.get('user', None):
            session['user'] = User.query.get(session['user_id'])
        g.user = session['user']
        g.oauth = lambda otype: OAuth.query.filter_by(oauth_type=otype, uid=g.user.id).first()

@app.after_request
def after_request(response):
    db_session.remove()
    return response

