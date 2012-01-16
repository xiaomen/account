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
        return oauth_info.oauth_token, oauth_info.oauth_secret

@renren_oauth.route('/Login')
def login():
    next_url = url_for('account.register')
    if g.user:
        if g.oauth('renren'):
            return redirect(request.referrer or url_for('index'))
        next_url = url_for('account.bind')

    return renren.authorize(callback=url_for('renren_oauth.authorized'), next_url=next_url)

@renren_oauth.route('/Authorized')
@renren.authorized_handler
def authorized(resp):
    next_url = request.args.get('state') or url_for('index')
    if resp is None:
        return redirect(next_url)
    print resp
    oauth = OAuth.query.filter_by(oauth_uid=resp['renren_user_id']).first()
    if oauth is None:
        oauth = OAuth(None, resp['renren_user_id'], 'renren')

    oauth.oauth_token = resp['access_token']
    oauth.oauth_secret = resp['access_token']
    if not g.user and oauth.uid:
        session['user_id'] = oauth.uid
        return redirect(url_for('index'))
    session['from_oauth'] = oauth
    return redirect(next_url)

