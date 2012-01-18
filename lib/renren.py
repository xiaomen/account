#!/usr/bin/python
# encoding: UTF-8

__all__ = ['renren']

import os
import config
from base import BasicOAuth

class RenrenOAuth(BasicOAuth):
    pass

renren = RenrenOAuth('renren',
    base_url='http://api.renren.com/restserver.do',
    request_token_url=None,
    access_token_url='https://graph.renren.com/oauth/token',
    authorize_url='https://graph.renren.com/oauth/authorize',
    access_token_method='POST',
    consumer_key=config.RENREN_APP_KEY,
    consumer_secret=config.RENREN_APP_SECRET
)
