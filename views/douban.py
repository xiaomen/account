#!/usr/bin/python
# encoding: UTF-8

import logging
from models import *
from lib.douban import douban
from flask import Blueprint, g, session, \
        request, redirect, url_for

logger = logging.getLogger(__name__)

douban_oauth = Blueprint('douban_oauth', __name__)

@douban.tokengetter
def get_douban_token():
    if g.user:
        oauth_info = g.oauth('douban')
        if not oauth_info:
            return
        return oauth_info.oauth_token, oauth_info.oauth_secret

@douban_oauth.route('/Login')
def login():
    next_url = url_for('account.register')
    if g.user:
        if g.oauth('douban'):
            return redirect(request.referrer or url_for('index'))
        next_url = url_for('account.bind')

    return douban.authorize(callback=url_for('douban_oauth.authorized'), next_url=next_url)

@douban_oauth.route('/Authorized')
@douban.authorized_handler
def authorized(resp):
    next_url = request.args.get('state') or url_for('index')
    if resp is None:
        return redirect(next_url)

    oauth = OAuth.query.filter_by(oauth_uid=resp['douban_user_id']).first()
    if oauth is None:
        oauth = OAuth(None, resp['douban_user_id'], 'douban')

    oauth.oauth_token = resp['access_token']
    oauth.oauth_secret = resp['access_token']
    if not g.user and oauth.uid:
        session['user_id'] = oauth.uid
        return redirect(url_for('index'))
    session['from_oauth'] = oauth
    return redirect(next_url)

