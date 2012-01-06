#!/usr/bin/python
# encoding: UTF-8

__all__ = ['weibo']

import config
from flaskext.oauth import OAuth
from flask import Flask, session, g, \
    request, redirect

weibo = OAuth().remote_app('weibo',
    base_url='http://api.t.sina.com.cn',
    request_token_url='http://api.t.sina.com.cn/oauth/request_token',
    access_token_url='http://api.t.sina.com.cn/oauth/access_token',
    authorize_url='http://api.t.sina.com.cn/oauth/authorize',
    consumer_key=config.APP_KEY,
    consumer_secret=config.APP_SECRET
)

app = Flask('app')

@weibo.tokengetter
def get_weibo_token():
    uid = g.uid
    if uid is not None:
        return uid.oauth_token, uid.oauth_secret

@app.route('/Login/Weibo')
def weibo_login():
    return weibo.authorize(callback=url_for('oauth_authorized',
        next=request.args.get('next') or request.referrer or None))

@app.route('/Authorized/Weibo')
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

class dbobj():pass

