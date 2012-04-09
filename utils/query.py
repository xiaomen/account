#!/usr/local/bin/python2.7
#coding:utf-8

from flask import g
from redistore import redistore
from sheep.api.cache import cache
from validators import check_domain

from models.mail import Mail
from models.account import User, Forget, OAuth

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

@cache('mail:unread:{to_uid}', 300)
def get_unread_mail_count(to_uid):
    return get_mail_by(to_uid=to_uid, is_read=0).count()

@cache('mail:recv:{uid}', 300)
def get_mail_recv_all(uid):
    return get_mail_by(to_uid=uid).all()

@cache('mail:view:{mid}', 300)
def get_mail(mid):
    try:
        mid = int(mid)
        return Mail.query.get(mid)
    except:
        return None

@cache('mail:sent:{uid}', 300)
def get_mail_sent_all(uid):
    return get_mail_by(from_uid=uid).all()

def get_mail_by(**kw):
    return Mail.query.filter_by(**kw)

def get_oauth_by(**kw):
    return OAuth.query.filter_by(**kw).first()

def get_user_by(**kw):
    return User.query.filter_by(**kw)

