#!/usr/bin/python
# encoding: UTF-8

import os
import json
import base64
import logging
from flaskext.oauth import *
from flask import g, redirect, request

logger = logging.getLogger(__name__)

class BasicOAuth(OAuthRemoteApp):
    def __init__(self, name, base_url,
                 request_token_url,
                 access_token_url, authorize_url,
                 consumer_key, consumer_secret,
                 request_token_params=None,
                 access_token_method='GET'):
        super(BasicOAuth, self).__init__(None, name, base_url,
                 request_token_url,
                 access_token_url, authorize_url,
                 consumer_key, consumer_secret,
                 request_token_params,
                 access_token_method)

    def authorize(self, callback=None, next_url=None):
        assert callback is not None, 'Callback is required OAuth2'
        csrf = base64.encodestring(os.urandom(10)).strip()
        params = dict(self.request_token_params)
        params['redirect_uri'] = callback
        params['client_id'] = self.consumer_key
        params['state'] = csrf
        params['response_type'] = 'code'
        g.session[self.name + '_oauthredir'] = callback
        g.session[self.name + '_oauthnext'] = next_url
        g.session[self.name + '_oauthcsrf'] = csrf
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
        return self.check_oauth_response(resp, content)

    def check_oauth_response(self, resp, content):
        try:
            data = json.loads(content)
            if resp['status'] != '200':
                raise OAuthException('Invalid response from ' + self.name, data)
            return data
        except Exception, e:
            logger.exception('oauth2_response_error')
            return None

    def get_request_token(self):
        assert self.tokengetter_func is not None, 'missing tokengetter function'
        rv = self.tokengetter_func()
        if rv is None:
            rv = g.session.get(self.name + '_oauthtok')
            if rv is None:
                raise OAuthException('No token available')
        if not isinstance(rv, tuple):
            #ugly design
            rv = (rv, '')
        return oauth2.Token(*rv)

    def request(self, url, data=None, headers=None, format='urlencoded',
                method='GET', content_type=None):
        headers = dict(headers or {})
        client = self.make_client()
        url = self.expand_url(url)
        if method == 'GET':
            assert format == 'urlencoded'
            if data is not None:
                url = add_query(url, data)
                data = None
        else:
            if content_type is None:
                data, content_type = encode_request_data(data, format)
            if content_type is not None:
                headers['Content-Type'] = content_type

        resp, content = client.request(url, method=method,
                                             body=data or '',
                                             headers=headers)
        #TODO access_token 过期，redirect到auth路径重新OOXX
        #对于豆瓣的oauth可以直接把路径计算为next_url
        return OAuthResponse(resp, content)
