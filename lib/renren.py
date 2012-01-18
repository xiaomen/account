#!/usr/bin/python
# encoding: UTF-8

__all__ = ['renren']

import os
import config
import hashlib
from base import BasicOAuth, OAuthResponse, encode_request_data

def make_sig(data):
    keys = data.keys()
    keys.sort()
    s = ''.join(['%s=%s' % (k, data[k]) for k in keys])
    s += config.RENREN_APP_SECRET
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()

class RenrenOAuth(BasicOAuth):
    def request(self, api, data=None, headers=None):
        headers = dict(headers or {})
        client = self.make_client()
        base_data = {
            'method': api,
            'v': '1.0',
            'format': 'json',
        }
        base_data.update(data)
        base_data['sig'] = make_sig(base_data)
        data, content_type = encode_request_data(data, 'urlencoded')
        if content_type is not None:
            headers['Content-Type'] = content_type
        resp, content = client.request(self.base_url, method='POST',
                                             body=data,
                                             headers=headers)
        return OAuthResponse(resp, content)

renren = RenrenOAuth('renren',
    base_url='http://api.renren.com/restserver.do',
    request_token_url=None,
    access_token_url='https://graph.renren.com/oauth/token',
    authorize_url='https://graph.renren.com/oauth/authorize',
    access_token_method='POST',
    consumer_key=config.RENREN_APP_KEY,
    consumer_secret=config.RENREN_APP_SECRET
)
