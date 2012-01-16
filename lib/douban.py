#!/usr/bin/python
# encoding: UTF-8

__all__ = ['douban']

import os
import json
import config
from flask import session, redirect, request
from flaskext.oauth import OAuthRemoteApp, add_query, \
        parse_response, OAuthException

class DoubanOAuth(OAuthRemoteApp):
    def authorize(self, callback=None, next_url=None):
        assert callback is not None, 'Callback is required OAuth2'
        params = dict(self.request_token_params)
        params['redirect_uri'] = 'http://'+request.environ['HTTP_HOST'] + callback
        params['client_id'] = self.consumer_key
        params['state'] = next_url
        params['response_type'] = 'code'
        session[self.name + '_oauthredir'] = callback
        url = add_query(self.expand_url(self.authorize_url), params)
        return redirect(url)

    def handle_oauth2_response(self):
        remote_args = {
            'code':             request.args.get('code'),
            'client_id':        self.consumer_key,
            'client_secret':    self.consumer_secret,
            'redirect_uri':     session.get(self.name + '_oauthredir'),
            'grant_type':       'authorization_code',
        }
        url = add_query(self.expand_url(self.access_token_url), remote_args)
        resp, content = self._client.request(url, self.access_token_method)
        data = json.loads(content)
        if resp['status'] != '200':
            raise OAuthException('Invalid response from ' + self.name, data)
        return data

douban = DoubanOAuth(None, 'douban',
    base_url='http://api.douban.com',
    request_token_url=None,
    access_token_url='https://www.douban.com/service/auth2/token',
    authorize_url='https://www.douban.com/service/auth2/auth',
    access_token_method='POST',
    consumer_key=config.DOUBAN_APP_KEY,
    consumer_secret=config.DOUBAN_APP_SECRET
)

def GET(path, param):
    url = os.path.join(path, param)
    return douban.get(url)
