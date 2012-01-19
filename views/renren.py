#!/usr/bin/python
# encoding: UTF-8

import logging
from models import *
from lib.renren import renren
from flask import Blueprint, g, session, \
        request, redirect, url_for

logger = logging.getLogger(__name__)

renren_oauth = Blueprint('renren_oauth', __name__)

@renren.tokengetter
def get_renren_token():
    if g.user:
        oauth_info = g.oauth('renren')
        if not oauth_info:
            return
        return oauth_info.oauth_token

@renren_oauth.route('/Login')
def login():
    next_url = url_for('account.register')
    if g.user:
        if g.oauth('renren'):
            return redirect(request.referrer or url_for('index'))
        next_url = url_for('account.bind')
    callback = 'http://%s%s' % (request.environ['HTTP_HOST'], url_for('renren_oauth.authorized'))
    return renren.authorize(callback, next_url)

@renren_oauth.route('/Authorized')
@renren.authorized_handler
def authorized(resp):
    csrf = session.pop('renren_oauthcsrf', None)
    if request.args.get('state') !=  csrf:
        return redirect(url_for('index'))
    next_url = session.pop('renren_oauthnext') or url_for('index')

    if resp is None:
        return redirect(next_url)

    oauth = OAuth.query.filter_by(oauth_uid=resp['user']['id']).first()
    if oauth is None:
        oauth = OAuth(None, resp['user']['id'], 'renren')

    oauth.oauth_token = resp['access_token']
    if not g.user and oauth.uid:
        session['user_id'] = oauth.uid
        return redirect(url_for('index'))
    session['from_oauth'] = oauth
    return redirect(next_url)
