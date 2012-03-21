#!/usr/local/bin/python2.7
#coding:utf-8

from flask import g
from models import db, User

def get_current_user():
    if not g.session or not g.session.get('user_id') or not g.session.get('user_token'):
        return None
    user = User.query.get(g.session['user_id'])
    if not user or g.session['user_token'] != user.token:
        return None
    return user
