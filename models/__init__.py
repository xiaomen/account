#!/usr/bin/python
# encoding: UTF-8

#from .mail import *
from .topic import *
from .account import *

def init_db(app):
    #init_mail_db(app)
    init_topic_db(app)
    init_account_db(app)

