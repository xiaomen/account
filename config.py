#!/usr/local/bin/python2.7
#coding:utf-8

DEBUG = True
SECRET_KEY = 'sheep!@$user!#$%^'

QQ_APP_KEY = '100241976'
QQ_APP_SECRET = '90b36f781da7ea1788278c105e2beecf'

WEIBO_APP_KEY = '619662253'
WEIBO_APP_SECRET = 'b1d02f2ff16aec904d835d34bc926ae7'

DOUBAN_APP_KEY = '0c8de809d0ca774525a9b81d725f65cf'
DOUBAN_APP_SECRET = 'a5ab8d4c622d0f82'

RENREN_APP_KEY = '7d153784732c4400aa6cef67d3dc3079'
RENREN_APP_SECRET = '1510ca7f69f84379b3655032b86d3435'

OAUTH_REDIRECT_DOMAIN = 'http://account.xiaomen.co'

DATABASE_URI = 'mysql://'

SESSION_KEY = 'xid'
SESSION_COOKIE_DOMAIN = '.xiaomen.co'

SMTP_SERVER = 'smtp.126.com'
SMTP_USER = 'xiaomenco@126.com'
SMTP_PASSWORD = 'ZhaoHuiMiMa!@#'

try:
    from local_config import *
except:
    pass
