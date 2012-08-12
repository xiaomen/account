#!/usr/local/bin/python2.7
#coding:utf-8

from flask import g
from sheep.api.cache import cache
from validators import check_domain
from helper import gen_list_page_obj
from werkzeug.exceptions import NotFound

from config import PAGE_NUM
from models.mail import Mail
from models.account import User, Forget, OAuth

@cache('account:{username}', 300)
def get_user(username):
    try:
        username = int(username)
        if username <= 0:
            return None
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

@cache('mail:inbox:count:{to_uid}', 300)
def get_inbox_count(to_uid):
    return get_mail_by(to_uid=to_uid).count()

@cache('mail:outbox:count:{from_uid}', 300)
def get_outbox_count(from_uid):
    return get_mail_by(from_uid=from_uid).count()

@cache('mail:inbox:{uid}:{page}', 300)
def get_inbox_mail(uid, page):
    try:
        page = int(page)
        uid = int(uid)
        page_obj = Mail.get_inbox_page(uid, page, per_page=PAGE_NUM)
        list_page = gen_list_page_obj(page_obj)
        return list_page
    except NotFound, e:
        raise e
    except Exception, e:
        print e
        return None

@cache('mail:outbox:{uid}:{page}', 300)
def get_outbox_mail(uid, page):
    try:
        page = int(page)
        uid = int(uid)
        page_obj = Mail.get_outbox_page(uid, page, per_page=PAGE_NUM)
        list_page = gen_list_page_obj(page_obj)
        return list_page
    except NotFound, e:
        raise e
    except Exception, e:
        return None

@cache('mail:view:{mid}', 300)
def get_mail(mid):
    try:
        mid = int(mid)
        return Mail.query.get(mid)
    except Exception, e:
        return None

def get_mail_by(**kw):
    return Mail.query.filter_by(**kw)

def get_oauth_by(**kw):
    return OAuth.query.filter_by(**kw).first()

def get_user_by(**kw):
    return User.query.filter_by(**kw)

def get_current_user():
    if not g.session or not g.session.get('user_id') or not g.session.get('user_token'):
        return None
    user = get_user(g.session['user_id'])
    if g.session['user_token'] != user.token:
        return None
    return user

