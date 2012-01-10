#!/usr/bin/python
# encoding: UTF-8

from lib.weibo import weibo
from flask import Flask, session, g, \
    request, redirect, url_for

@weibo.tokengetter
def get_weibo_token():
    uid = g.uid
    if uid is not None:
        return uid.oauth_token, uid.oauth_secret

def weibo_login():
    session.pop('user_id', None)
    return weibo.authorize(callback=url_for('weibo_authorized',
        next=request.args.get('next') or request.referrer or None))

@weibo.authorized_handler
def weibo_authorized(resp):
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
