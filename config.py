#!/usr/local/bin/python2.7
#coding:utf-8

DEBUG = True
SECRET_KEY = 'sheep!@$user!#$%^'

APP_KEY = '619662253'
APP_SECRET = 'b1d02f2ff16aec904d835d34bc926ae7'

DATABASE_URI = 'mysql://root@localhost:3306/user'

try:
    from local_config import *
except:
    pass
