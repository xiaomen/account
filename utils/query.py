#!/usr/local/bin/python2.7
#coding:utf-8

from flask import g
from models import db, User, Forget

def get_current_user():
    if not g.session or not g.session.get('user_id') or not g.session.get('user_token'):
        return None
    user = get_user(g.session['user_id'])
    if not user or g.session['user_token'] != user.token:
        return None
    return user

#cache
def get_user(username):
    try:
        username = int(username)
        return User.query.get(username)
    except:
        if check_domain(username):
            return None
        return get_user_by(domain=username).first()

#cache
def get_user_by(**kw):
    return User.query.filter_by(**kw)

#cache
def get_forget_by(**kw):
    return Forget.query.filter_by(**kw)
