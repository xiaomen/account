#!/usr/bin/python
# encoding: UTF-8

import logging
from models import *
from lib.weibo import weibo
from flask import Flask, session, g, \
    request, redirect, url_for

logger = logging.getLogger(__name__)

@weibo.tokengetter
def get_weibo_token():
    user = g.user
    if user is not None:
        return user.oauth_token, user.oauth_secret

def weibo_login():
    session.pop('user_id', None)
    return weibo.authorize(callback=url_for('weibo_authorized',
        next=request.args.get('next') or request.referrer or None))

@weibo.authorized_handler
def weibo_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        return redirect(next_url)

    user = User.query.filter_by(uid=resp['user_id']).first()
    if user is None:
        user = User(resp['user_id'])
        db_session.add(user)

    user.oauth_token = resp['oauth_token']
    user.oauth_secret = resp['oauth_token_secret']
    db_session.commit()
    session['user_id'] = user.uid
    return redirect(next_url)

