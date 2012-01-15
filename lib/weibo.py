#!/usr/bin/python
# encoding: UTF-8

__all__ = ['weibo']

import os
import config
from flaskext.oauth import OAuth

weibo = OAuth().remote_app('weibo',
    base_url='http://api.t.sina.com.cn',
    request_token_url='http://api.t.sina.com.cn/oauth/request_token',
    access_token_url='http://api.t.sina.com.cn/oauth/access_token',
    authorize_url='http://api.t.sina.com.cn/oauth/authorize',
    consumer_key=config.WEIBO_APP_KEY,
    consumer_secret=config.WEIBO_APP_SECRET
)

def GET(path, param):
    url = os.path.join(path, param + '.json')
    return weibo.get(url)
