#!/usr/bin/python
# encoding: UTF-8

__all__ = ['douban']

import os
import config
from flaskext.oauth import OAuth

douban = OAuth().remote_app('douban',
    base_url='http://api.douban.com',
    request_token_url='http://www.douban.com/service/auth/request_token',
    access_token_url='http://www.douban.com/service/auth/access_token',
    authorize_url='http://www.douban.com/service/auth/authorize',
    consumer_key=config.DOUBAN_APP_KEY,
    consumer_secret=config.DOUBAN_APP_SECRET
)

def GET(path, param):
    url = os.path.join(path, param)
    return douban.get(url)
