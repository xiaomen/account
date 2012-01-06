#!/usr/bin/python
# encoding: UTF-8

import views
import config
from models import *
from lib.weibo import weibo
from sheep.api.statics import static_files
from flask import Flask, render_template, redirect, \
    request, session, url_for, g

app = Flask(__name__)
app.debug = config.DEBUG
app.secret_key = config.SECRET_KEY
app.jinja_env.filters['s_files'] = static_files

init_db()

@app.route('/')
def index():
    if g.uid is None:
        return render_template('index.html')
    else:
        print weibo.get("/users/show/" + g.uid.user_id + ".json").data
        return '<a href="/Logout">Logout</a>'

@app.route('/Logout')
def logout():
    session.pop('user_id', None)
    return redirect(request.referrer or url_for('index'))

@app.before_request
def before_request():
    g.uid = None
    if 'user_id' in session:
        g.uid = session['user_id']

app.add_url_rule('/Login/Weibo', view_func=views.weibo.weibo_login)
app.add_url_rule('/Authorized/Weibo', view_func=views.weibo.weibo_authorized)
