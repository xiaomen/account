#!/usr/bin/python
# encoding: UTF-8

from config import APP_KEY, APP_SECRET
from sheep.api.statics import static_files

from flaskext.oauth import OAuth
from flask import Flask, render_template, redirect, request, session, url_for

app = Flask(__name__)
app.debug = True
app.jinja_env.filters['s_files'] = static_files
app.secret_key = 'sheep!@$user!#$%^'

oauth = OAuth()

weibo = oauth.remote_app('weibo',
    base_url='http://api.t.sina.com.cn',
    request_token_url='http://api.t.sina.com.cn/oauth/request_token',
    access_token_url='http://api.t.sina.com.cn/oauth/access_token',
    authorize_url='http://api.t.sina.com.cn/oauth/authorize',
    consumer_key=APP_KEY,
    consumer_secret=APP_SECRET
)

@app.route('/')
def index():
    if session.get('isLogin', None):
        return render_template('index.html')
    else:
        return 'success'

@app.route('/Login')
def login():
    session['isLogin'] = True
    return 'logined'

@app.route('/Login/Weibo')
def weibo_login():
    return weibo.authorize(callback=url_for('oauth_authorized',
        next=request.args.get('next') or request.referrer or None))

@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        print u'You denied the request to sign in.'
        return redirect(next_url)
    session['weibo_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
    )
    session['isLogin'] = True
    print 'You were signed in'
    return redirect(next_url)

@twitter.tokengetter
def get_weibo_token():
    if not session.get('isLogin', None):
        return session['oauth_token'], session['user.oauth_secret']
