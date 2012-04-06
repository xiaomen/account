#!/usr/local/bin/python2.7
#coding:utf-8

from flask import g
from redistore import redistore
from sheep.api.cache import cache
from validators import check_domain
from models import db, User, Forget, OAuth

def get_current_user():
    if not g.session or not g.session.get('user_id') or not g.session.get('user_token'):
        return None
    token = redistore.get('account|uid-%s|token' % g.session['user_id'])
    if not token or g.session['user_token'] != token:
        return None
    return get_user(g.session['user_id'])

@cache('account:{username}', 300)
def get_user(username):
    try:
        username = int(username)
        return User.query.get(username)
    except:
        if check_domain(username):
            return None
        return get_user_by_domain(domain=username)

@cache('account:{domain}', 300)
def get_user_by_domain(domain):
    return get_user_by(domain=domain).first()

@cache('account:{email}', 300)
def get_user_by_email(email):
    return get_user_by(email=email).first()

@cache('account:{stub}', 100)
def get_forget_by_stub(stub):
    return Forget.query.filter_by(stub=stub).first()

def get_oauth_by(**kw):
    return OAuth.query.filter_by(**kw).first()

def get_user_by(**kw):
    return User.query.filter_by(**kw)
