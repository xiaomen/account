#!/usr/bin/python
# encoding: UTF-8

import logging
from models import *
from lib.qq import qq
from flask import Blueprint, g, session, \
        request, redirect, url_for

logger = logging.getLogger(__name__)

qq_oauth = Blueprint('qq_oauth', __name__)

@qq.tokengetter
def get_qq_token():
    if g.user:
        oauth_info = g.oauth('qq')
        if not oauth_info:
            return
        return oauth_info.oauth_token

@qq_oauth.route('/Login')
def login():
    next_url = url_for('account.register')
    if g.user:
        if g.oauth('qq'):
            return redirect(request.referrer or url_for('index'))
        next_url = url_for('account.bind')
    callback = 'http://%s%s' % (request.environ['HTTP_HOST'], url_for('qq_oauth.authorized'))
    return qq.authorize(callback, next_url)

@qq_oauth.route('/Authorized')
@qq.authorized_handler
def authorized(resp):
    csrf = session.pop('qq_oauthcsrf', None)
    if request.args.get('state') !=  csrf:
        return redirect(url_for('index'))
    next_url = session.pop('qq_oauthnext') or url_for('index')

    #TODO None redirect to index
    if resp is None:
        return redirect(next_url)

    oauth = OAuth.query.filter_by(oauth_uid=resp['openid']).first()
    if oauth is None:
        oauth = OAuth(None, resp['openid'], 'qq')

    oauth.oauth_token = resp['access_token']
    if not g.user and oauth.uid:
        session['user_id'] = oauth.uid
        return redirect(url_for('index'))
    session['from_oauth'] = oauth
    return redirect(next_url)
