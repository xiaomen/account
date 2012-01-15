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
        return oauth_info.oauth_token, oauth_info.oauth_secret

@weibo_oauth.route('/Login')
def login():
    if g.user and g.oauth('weibo'):
        return redirect(request.referrer or url_for('index'))
    return weibo.authorize(callback=url_for('weibo_oauth.authorized',
        next=url_for('account.register')))

@weibo_oauth.route('/Authorized')
@weibo.authorized_handler
def authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        return redirect(next_url)

    oauth = OAuth.query.filter_by(oauth_uid=resp['user_id']).first()
    if oauth is None:
        oauth = OAuth(None, resp['user_id'], 'weibo')
        db_session.add(oauth)

    oauth.oauth_token = resp['oauth_token']
    oauth.oauth_secret = resp['oauth_token_secret']
    if g.user:
        oauth.uid = g.user.id
    db_session.commit()
    if oauth.uid:
        session['user_id'] = oauth.uid
        return redirect(url_for('index'))
    session['from_oauth'] = oauth
    return redirect(next_url)

