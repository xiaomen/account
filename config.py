#!/usr/local/bin/python2.7
#coding:utf-8

DEBUG = False
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

SMTP_SERVER = 'smtp.qq.com'
SMTP_USER = 'service@xiaomen.co'
SMTP_PASSWORD = 'xiaomenkou!@#$%^'

FORGET_STUB_EXPIRE = 30*60

PAGE_NUM = 5

TOKEN_TOKEN = 'account:token:token:%s'
TOKEN_UID = 'account:token:uid:%d'
TOKEN_LENGTH = 6
TOKEN_EXPIRE = 3600

FORGET_EMAIL_TITLE = '[校门口]取回密码'

MAX_CONTENT_LENGTH = 512 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

WEIXIN_TOKEN = "xiaomenco"

try:
    from local_config import *
except:
    pass
