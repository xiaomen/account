#!/usr/bin/python
# encoding: UTF-8

__all__ = ['douban']

import os
import config
from base import BasicOAuth

class DoubanOAuth(BasicOAuth):
    pass

douban = DoubanOAuth('douban',
    base_url='https://api.douban.com',
    request_token_url=None,
    access_token_url='https://www.douban.com/service/auth2/token',
    authorize_url='https://www.douban.com/service/auth2/auth',
    access_token_method='POST',
    consumer_key=config.DOUBAN_APP_KEY,
    consumer_secret=config.DOUBAN_APP_SECRET
)
