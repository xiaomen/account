#!/usr/local/bin/python2.7
#coding:utf-8

from sheep.api.cache import cache
from utils.helper import gen_list_page_obj
from werkzeug.exceptions import NotFound

from config import PAGE_NUM
from models.mail import Mail

@cache('mail:unread:{to_uid}', 300)
def get_unread_mail_count(to_uid):
    return get_mail_by(to_uid=to_uid, is_read=0, inbox=1).count()

@cache('mail:inbox:count:{to_uid}', 300)
def get_inbox_count(to_uid):
    return get_mail_by(to_uid=to_uid, inbox=1).count()

@cache('mail:outbox:count:{from_uid}', 300)
def get_outbox_count(from_uid):
    return get_mail_by(from_uid=from_uid, outbox=1).count()

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
        import traceback
        traceback.print_exc()

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
        import traceback
        traceback.print_exc()

@cache('mail:view:{mid}', 300)
def get_mail(mid):
    try:
        mid = int(mid)
        return Mail.query.get(mid)
    except Exception:
        return None

def get_mail_by(**kw):
    return Mail.query.filter_by(**kw)

create_mail = Mail.create
