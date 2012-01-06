#!/usr/bin/python
# encoding: UTF-8

from lib.weibo import APIClient
from config import APP_KEY, APP_SECRET, CALLBACK_URL
from flask import Flask, render_template, redirect, request, session
from sheep.api.statics import static_files

app = Flask(__name__)
app.debug = True
app.jinja_env.filters['s_files'] = static_files
app.secret_key = 'sheep!@$user!#$%^'

@app.route('/')
def index():
    if session.get('isLogin') is None:
        return render_template('index.html')
    else:
        code = request.form.get('code')
        client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
        r = client.request_access_token(code)
        access_token = r.access_token
        expires_in = r.expires_in
        client.set_access_token(access_token, expires_in)
        return client.get.statuses__user_timeline()

@app.route('/Login')
def login():
    session['isLogin'] = 1
    return redirect('/')

@app.route('/weibo')
def weibo_login():
    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    url = client.get_authorize_url()
    return redirect(url)

