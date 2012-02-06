#!/usr/bin/python
# encoding: UTF-8

import os
import config
import logging

from models import *
from views.oauth import oauth
from views.account import account
from sheep.api.permdir import permdir
from sheep.api.statics import static_files
from sheep.api.sessions import SessionMiddleware
from werkzeug.contrib.sessions import FilesystemSessionStore

from flaskext.csrf import csrf
from flask import Flask, render_template, \
        request, url_for, g

app = Flask(__name__)
app.debug = config.DEBUG
app.secret_key = config.SECRET_KEY
app.jinja_env.filters['s_files'] = static_files

app.config.update(
    SQLALCHEMY_DATABASE_URI = config.DATABASE_URI,
    SQLALCHEMY_POOL_SIZE = 1000,
    SQLALCHEMY_POOL_RECYCLE = True,
    SESSION_COOKIE_DOMAIN = config.SESSION_COOKIE_DOMAIN,
)

oauth.register_blueprints(app)
app.register_blueprint(account, url_prefix='/account')
logger = logging.getLogger(__name__)

init_db(app)
csrf(app)
app.wsgi_app = SessionMiddleware(app.wsgi_app, \
        FilesystemSessionStore(), \
        cookie_name=config.SESSION_KEY, cookie_path='/', \
        cookie_domain=config.SESSION_COOKIE_DOMAIN)

@app.route('/')
def index():
    if not g.user:
        return render_template('index.html', login_url=url_for('account.login'))
    user = User.query.get(g.session['user_id'])
    return render_template('index.html', login=1, \
            user_name=user.name,
            user_email=user.email)

@app.before_request
def before_request():
    g.session = request.environ['xiaomen.session']
    g.user = 'user_id' in g.session and g.session['user_id']

@app.errorhandler(404)
def page_not_found(e):
    return render_template('40x.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('40x.html'), 500

