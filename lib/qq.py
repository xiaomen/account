#!/usr/bin/python
# encoding: UTF-8

__all__ = ['qq']

import os
import json
import config
import urllib2
import logging
from base import BasicOAuth

logger = logging.getLogger(__name__)

class QQOAuth(BasicOAuth):
    def check_oauth_response(self, resp, content):
        try:
            if resp['status'] != '200':
                raise OAuthException('Invalid response from ' + self.name, content)
            data = {}
            for c in content.split('&'):
                k, v = c.split('=')
                data[k] = v
            openid_url = self.base_url + 'oauth2.0/me?access_token=' + data['access_token']
            content = urllib2.urlopen(openid_url).read().strip()
            content = json.loads(content[content.find('(')+1:content.find(')')].strip())
            data.update(content)
            return data
        except Exception, e:
            logger.exception('oauth2_response_error')
            return None

qq = QQOAuth('qq',
    base_url='https://graph.qq.com/',
    request_token_url=None,
    access_token_url='https://graph.qq.com/oauth2.0/token',
    authorize_url='https://graph.qq.com/oauth2.0/authorize',
    access_token_method='GET',
    consumer_key=config.QQ_APP_KEY,
    consumer_secret=config.QQ_APP_SECRET
)
