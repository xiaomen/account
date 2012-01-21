#!/usr/local/bin/python2.7
#coding:utf-8

import logging
from models import *
from utils import bind_oauth
from flask import Blueprint, g, session, \
        request, redirect, url_for

logger = logging.getLogger(__name__)

class Base_OAuth_Login(object):
    def __init__(self, name, oauth_obj, uid_str='uid', token_str='access_token'):
        self.name = name
        self.oauth_obj = oauth_obj
        self.uid_str = uid_str
        self.token_str = token_str

    def get_token(self):
        if g.user:
            oauth_info = g.oauth(self.name)
            if not oauth_info:
                return
            return oauth_info.oauth_token

    def login(self):
        next_url = url_for('account.register')
        if g.user:
            if g.oauth(self.name):
                return redirect(request.referrer or url_for('index'))
            next_url = url_for('account.bind')
        callback = 'http://%s%s' % (request.environ['HTTP_HOST'], url_for('%s_oauth.authorized' % self.name))
        return self.oauth_obj.authorize(callback, next_url)

    def authorized(self, resp):
        csrf = session.pop('%s_oauthcsrf' % self.name, None)
        if request.args.get('state') !=  csrf:
            return redirect(url_for('index'))
        next_url = session.pop('%s_oauthnext' % self.name) or url_for('index')
        logger.info(resp)
        uid = resp.get(self.uid_str, None)
        token = resp.get(self.token_str, None)
        if not resp or not uid or not token:
            return redirect(next_url)

        oauth = OAuth.query.filter_by(oauth_uid=resp[self.uid_str]).first()
        if oauth is None:
            oauth = OAuth(None, resp[self.uid_str], self.name)

        old_token = oauth.oauth_token
        oauth.oauth_token = resp[self.token_str]
        if not g.user and oauth.uid:
            session['user_id'] = oauth.uid
            if old_token != oauth.oauth_token:
                logger.info(old_token)
                logger.info(oauth.oauth_token)
                self.update_token(oauth)
            return redirect(url_for('index'))
        session['from_oauth'] = oauth
        return redirect(next_url)

    def update_token(self, oauth):
        db.session.add(oauth)
        db.session.commit()
