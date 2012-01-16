#!/usr/bin/python
# encoding: UTF-8

__all__ = ['renren']

import os
import json
import config
from flask import session, redirect, request
from flaskext.oauth import *

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
        return OAuthResponse(resp, r'''%s''' % content)

renren = DoubanOAuth(None, 'renren',
    base_url='http://api.renren.com/restserver.do',
    request_token_url=None,
    access_token_url='https://graph.renren.com/oauth/token',
    authorize_url='https://graph.renren.com/oauth/authorize',
    access_token_method='POST',
    consumer_key=config.DOUBAN_APP_KEY,
    consumer_secret=config.DOUBAN_APP_SECRET
)

def GET(path, param):
    url = os.path.join(path, param+'?alt=json')
    access_token = renren.tokengetter_func()
    if not access_token:
        return None
    return renren.get(url, headers={'Authorization': 'Bearer %s' % access_token[0]})

