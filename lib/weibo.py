#!/usr/bin/python
# encoding: UTF-8

__all__ = ['weibo']

import config

weibo = OAuth().remote_app('weibo',
    base_url='http://api.t.sina.com.cn',
    request_token_url='http://api.t.sina.com.cn/oauth/request_token',
    access_token_url='http://api.t.sina.com.cn/oauth/access_token',
    authorize_url='http://api.t.sina.com.cn/oauth/authorize',
    consumer_key=config.APP_KEY,
    consumer_secret=config.APP_SECRET
)
