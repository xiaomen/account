#!/usr/bin/python
# encoding: UTF-8

__all__ = ['douban']

import os
import config
from base import BasicOAuth, OAuthResponse, encode_request_data

class DoubanOAuth(BasicOAuth):
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
        content = content.replace('\'', '\"')
        return OAuthResponse(resp, content)

douban = DoubanOAuth('douban',
    base_url='https://api.douban.com',
    request_token_url=None,
    access_token_url='https://www.douban.com/service/auth2/token',
    authorize_url='https://www.douban.com/service/auth2/auth',
    access_token_method='POST',
    consumer_key=config.DOUBAN_APP_KEY,
    consumer_secret=config.DOUBAN_APP_SECRET
)
