#!/usr/bin/python
# encoding: UTF-8

import config
from lib.weibo import weibo
from sheep.api.statics import static_files
from flask import Flask, render_template, redirect, \
    request, session, url_for, g

app = Flask(__name__)
app.debug = config.DEBUG
app.secret_key = config.SECRET_KEY
app.jinja_env.filters['s_files'] = static_files

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

@app.route('/Login/Weibo')
def weibo_login():
    return weibo.authorize(callback=url_for('oauth_authorized',
        next=request.args.get('next') or request.referrer or None))

@app.route('/oauth-authorized')
@weibo.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        return redirect(next_url)

    user = dbobj()
    user.oauth_token = resp['oauth_token']
    user.oauth_secret = resp['oauth_token_secret']
    user.user_id = resp['user_id']
    session['user_id'] = user
    return redirect(next_url)

@app.before_request
def before_request():
    g.uid = None
    if 'user_id' in session:
        g.uid = session['user_id']

class dbobj():pass
