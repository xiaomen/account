#!/usr/local/bin/python2.7
#coding:utf-8

import urllib
import logging

import config
from utils.account import account_login
from flask import g, session, request, \
        redirect, url_for

from query.account import get_user, get_oauth_by
from query.oauth import create_oauth

logger = logging.getLogger(__name__)

class Base_OAuth_Login(object):
    def __init__(self, name, oauth_obj, uid_str='uid', token_str='access_token'):
        self.name = name
        self.oauth_obj = oauth_obj
        self.uid_str = uid_str
        self.token_str = token_str

    def get_token(self):
        if g.current_user:
            oauth_info = get_oauth_by(oauth_type=self.name, uid=g.session['user_id'])
            if not oauth_info:
                return
            return oauth_info.oauth_token

    def login(self):
        next_url = url_for('account.register')
        if g.current_user:
            oauth_info = get_oauth_by(oauth_type=self.name, uid=g.session['user_id'])
            if oauth_info:
                return redirect(request.referrer or url_for('index'))
            next_url = url_for('account.bind')
        callback = '%s%s' % (config.OAUTH_REDIRECT_DOMAIN, url_for('%s_oauth.authorized' % self.name))
        return self.oauth_obj.authorize(callback, next_url)

    def authorized(self, resp):
        csrf = session.pop('%s_oauthcsrf' % self.name, None)
        state = request.args.get('state')
        if state and urllib.unquote(state) !=  csrf:
            return redirect(url_for('index'))
        if not session:
            return redirect(url_for('index'))
        next_url = session.pop('%s_oauthnext' % self.name) or url_for('index')
        logger.info(resp)
        if not resp or not resp.get(self.uid_str, None) \
                or not resp.get(self.token_str, None):
            return redirect(next_url)
        #safe escape
        #uid = resp.get(self.uid_str, None)
        token = resp.get(self.token_str, None)

        oauth = get_oauth_by(oauth_uid=resp[self.uid_str])
        if oauth is None:
            oauth = create_oauth(None, resp[self.uid_str], self.name)

        old_token = oauth.oauth_token
        oauth.oauth_token = token
        if not g.current_user and oauth.uid:
            #need profile!
            user = get_user(oauth.uid)
            if user:
                account_login(user)

                if old_token != oauth.oauth_token:
                    logger.info(old_token)
                    logger.info(oauth.oauth_token)
                    oauth.store()
                    self.update_token(oauth)

                return redirect(url_for('index'))

        session['from_oauth'] = oauth
        return redirect(next_url)

