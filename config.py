#!/usr/local/bin/python2.7
#coding:utf-8

DEBUG = True
SECRET_KEY = 'sheep!@$user!#$%^'

WEIBO_APP_KEY = '619662253'
WEIBO_APP_SECRET = 'b1d02f2ff16aec904d835d34bc926ae7'

DOUBAN_APP_KEY = '0c8de809d0ca774525a9b81d725f65cf'
DOUBAN_APP_SECRET = 'a5ab8d4c622d0f82'

DATABASE_URI = 'mysql://'

try:
    from local_config import *
except:
    pass
