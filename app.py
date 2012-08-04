#!/usr/bin/python
# encoding: UTF-8

import os
import time
import config
import logging
from functools import wraps
from werkzeug.useragents import UserAgent

from utils import *
from models import *

from views.api import api
from views.mail import mail
from views.oauth import oauth
from views.people import people
from views.account import account

from sheep.api.statics import static_files
from sheep.api.sessions import SessionMiddleware, \
    FilesystemSessionStore

import flask
from flaskext.csrf import csrf
from flask import Flask, \
        request, url_for, g, redirect

app = Flask(__name__)
app.debug = config.DEBUG
app.secret_key = config.SECRET_KEY
app.jinja_env.filters['s_files'] = static_files

app.config.update(
    SQLALCHEMY_DATABASE_URI = config.DATABASE_URI,
    SQLALCHEMY_POOL_SIZE = 100,
    SQLALCHEMY_POOL_TIMEOUT = 10,
    SQLALCHEMY_POOL_RECYCLE = 3600,
    SESSION_COOKIE_DOMAIN = config.SESSION_COOKIE_DOMAIN,
)

oauth.register_blueprints(app)
app.register_blueprint(account, url_prefix='/account')
app.register_blueprint(people, url_prefix='/people')
app.register_blueprint(mail, url_prefix='/mail')
app.register_blueprint(api, url_prefix='/api')

logger = logging.getLogger(__name__)

init_db(app)
csrf(app)
app.wsgi_app = SessionMiddleware(app.wsgi_app, \
        FilesystemSessionStore(), \
        cookie_name=config.SESSION_KEY, cookie_path='/', \
        cookie_domain=config.SESSION_COOKIE_DOMAIN)

def check_ua(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        ua = UserAgent(request.headers.get('User-Agent'))
        if ua.browser == 'msie':
            try:
                if int(float(ua.version)) < 8:
                    return render_template("noie.html")
            except:
                return render_template("noie.html")
        return method(*args, **kwargs) 
    return wrapper

def render_template(template_name, *args, **kwargs):
    ua = UserAgent(request.headers.get('User-Agent'))
    if ua.platform and ua.platform.lower() in ["android", "iphone"]:
        return flask.render_template("mobile/" + template_name, *args, **kwargs)
    return flask.render_template(template_name, *args, **kwargs)

@app.route('/')
@check_ua
def index():
    user = get_current_user()
    if not user:
        return render_template('index.html', login_url=url_for('account.login'))
    if user.domain:
        username = user.domain
    else:
        username = user.id

    return render_template('index.html', login=1, \
            user = user,
            unread_mail_count = get_unread_mail_count(user.id),
            my_url = url_for('people.show_people', username=username))

@app.before_request
def before_request():
    g.session = request.environ['xiaomen.session']

