#!/usr/bin/python
# encoding: UTF-8

__all__ = ['qq']

import os
import json
import config
import base64
import logging
from flask import session, redirect, request
from flaskext.oauth import *

logger = logging.getLogger(__name__)

class QQOAuth(OAuthRemoteApp):
    def authorize(self, callback=None, next_url=None):
        assert callback is not None, 'Callback is required OAuth2'
        csrf = base64.encodestring(os.urandom(10)).strip()
        params = dict(self.request_token_params)
        params['redirect_uri'] = callback
        params['client_id'] = self.consumer_key
        params['state'] = csrf
        params['response_type'] = 'code'
        session[self.name + '_oauthredir'] = callback
        session[self.name + '_oauthnext'] = next_url
        session[self.name + '_oauthcsrf'] = csrf
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
        data = json.loads(content[content.find('(')+1 : content.find(')')].strip())
        print data
        if data.get('error', None):
            logger.info(data)
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
        #TODO access_token 过期，redirect到auth路径重新OOXX
        #刷新token然后更新数据库，再进行请求
        return OAuthResponse(resp, r'''%s''' % content)

qq = QQOAuth(None, 'qq',
    base_url='https://graph.qq.com/',
    request_token_url=None,
    access_token_url='https://graph.qq.com/oauth2.0/token',
    authorize_url='https://graph.qq.com/oauth2.0/authorize',
    access_token_method='POST',
    consumer_key=config.QQ_APP_KEY,
    consumer_secret=config.QQ_APP_SECRET
)

def GET(path, param):
    url = os.path.join(path, param)
    access_token = qq.tokengetter_func()
    if not access_token:
        return None
    return qq.get(url, headers={'Authorization': 'Bearer %s' % access_token[0]})

