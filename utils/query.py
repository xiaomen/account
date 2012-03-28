#!/usr/local/bin/python2.7
#coding:utf-8

from flask import g
from sheep.api.cache import Cache
from validators import check_domain
from models import db, User, Forget, OAuth

def get_current_user():
    if not g.session or not g.session.get('user_id') or not g.session.get('user_token'):
        return None
    user = get_user(g.session['user_id'])
    if not user or g.session['user_token'] != user.token:
        return None
    return user

@Cache('account', 300)
def get_user(username):
    try:
        username = int(username)
        return User.query.get(username)
    except:
        if check_domain(username):
            return None
        return get_user_by(domain=username)

@Cache('account', 300)
def get_user_by(**kw):
    return User.query.filter_by(**kw).first()

@Cache('account', 100)
def get_forget_by(**kw):
    return Forget.query.filter_by(**kw).first()

def get_oauth_by(**kw):
    return OAuth.query.filter_by(**kw).first()
