#!/usr/bin/python
# encoding: UTF-8

import config
import logging
from models import *
from views.qq import qq_oauth
from views.weibo import weibo_oauth
from views.douban import douban_oauth
from views.renren import renren_oauth
from views.account import account
from sheep.api.statics import static_files
from flask import Flask, render_template, session, g

app = Flask(__name__)
app.debug = config.DEBUG
app.secret_key = config.SECRET_KEY
app.jinja_env.filters['s_files'] = static_files

app.config.update(
    SQLALCHEMY_DATABASE_URI = config.DATABASE_URI,
    SQLALCHEMY_POOL_SIZE = 1000,
    SQLALCHEMY_POOL_RECYCLE = True
)

app.register_blueprint(qq_oauth, url_prefix='/QQ')
app.register_blueprint(weibo_oauth, url_prefix='/Weibo')
app.register_blueprint(douban_oauth, url_prefix='/Douban')
app.register_blueprint(renren_oauth, url_prefix='/Renren')
app.register_blueprint(account, url_prefix='/Account')

logger = logging.getLogger(__name__)

init_db(app)

@app.route('/')
def index():
    if g.user is None:
        return render_template('index.html')
    else:
        logout = '<a href="/Account/Logout">Logout</a>'
        oauth_info = g.oauth('douban')
        values = {}
        if oauth_info:
            from lib import douban
            user_info = douban.GET("/people", "@me")
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

