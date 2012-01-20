#!/usr/local/bin/python2.7
#coding:utf-8

from models import db

def bind_oauth(oauth, uid):
    oauth.bind(uid)
    db.session.add(oauth)
    db.session.commit()
