#!/usr/bin/python
# encoding: UTF-8

import logging
from models import *
from lib.weibo import weibo
from flask import Blueprint, g, session, \
        request, redirect, url_for

logger = logging.getLogger(__name__)

weibo_oauth = Blueprint('weibo_oauth', __name__)

@weibo.tokengetter
def get_weibo_token():
    if g.user:
        oauth_info = g.oauth('weibo')
        if not oauth_info:
            return
        return oauth_info.oauth_token

@weibo_oauth.route('/Login')
def login():
    next_url = url_for('account.register')
    if g.user:
        if g.oauth('weibo'):
            return redirect(request.referrer or url_for('index'))
        next_url = url_for('account.bind')
    callback = 'http://%s%s' % (request.environ['HTTP_HOST'], url_for('weibo_oauth.authorized'))
    return weibo.authorize(callback, next_url)

@weibo_oauth.route('/Authorized')
@weibo.authorized_handler
def authorized(resp):
    csrf = session.pop('weibo_oauthcsrf', None)
    if request.args.get('state') !=  csrf:
        return redirect(url_for('index'))
    next_url = session.pop('weibo_oauthnext') or url_for('index')
    if resp is None:
        #TODO logger exception
        return redirect(next_url)

    oauth = OAuth.query.filter_by(oauth_uid=resp['uid']).first()
    if oauth is None:
        oauth = OAuth(None, resp['uid'], 'weibo')

    oauth.oauth_token = resp['access_token']
    if not g.user and oauth.uid:
        session['user_id'] = oauth.uid
        return redirect(url_for('index'))
    session['from_oauth'] = oauth
    return redirect(next_url)
