#!/usr/bin/python
# encoding: UTF-8

__all__ = ['weibo']

import os
import config
from base import BasicOAuth

class WeiboOAuth(BasicOAuth):
    pass

weibo = WeiboOAuth('weibo',
    base_url='https://api.weibo.com/2/',
    request_token_url=None,
    access_token_url='https://api.weibo.com/oauth2/access_token',
    authorize_url='https://api.weibo.com/oauth2/authorize',
    access_token_method='POST',
    consumer_key=config.WEIBO_APP_KEY,
    consumer_secret=config.WEIBO_APP_SECRET
)
