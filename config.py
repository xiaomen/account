#!/usr/local/bin/python2.7
#coding:utf-8

DEBUG = True
SECRET_KEY = 'sheep!@$user!#$%^'

WEIBO_APP_KEY = '619662253'
WEIBO_APP_SECRET = 'b1d02f2ff16aec904d835d34bc926ae7'

DOUBAN_APP_KEY = '066be7393f0d23391343b5abbd2769ab'
DOUBAN_APP_SECRET = '7f28390804c3654c'

DATABASE_URI = 'mysql://'

try:
    from local_config import *
except:
    pass
