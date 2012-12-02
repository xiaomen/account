#!/usr/local/bin/python2.7
#coding:utf-8

'''
用户有多少topics应该是存在另外一张表里面，
后期优化应考虑topic分页的时候用多个查询代替count锁表。
比如，先查用户有多少个topic，然后从topic表中limit查对应topic。
同理适用于reply，先从topic表中查到reply_count再分页。
'''

from sqlalchemy import and_
from sqlalchemy.sql.expression import desc

from config import PAGE_NUM
from models.topic import Topic, Reply, Mailr, create_topic, create_reply

def get_user_topics(uid, page):
    page_obj = Mailr.query.filter(and_(Mailr.uid==uid, Mailr.has_delete==0))
    page_obj = page_obj.order_by(desc(Mailr.last_time))
    page_obj = page_obj.paginate(page, per_page=PAGE_NUM)
    return page_obj

def get_user_replies(tid, page):
    page_obj = Reply.query.filter(Reply.tid==tid)
    page_obj = page_obj.order_by(desc(Reply.time))
    page_obj = page_obj.paginate(page, per_page=PAGE_NUM)
    return page_obj

def make_topic(uid, to_uid, title, content):
    #TODO clean cache!!!
    return create_topic(uid, to_uid, title, content)

def make_reply(sender, receiver, topic, content):
    return create_reply(sender, receiver, topic, content)

def mark_read(uid, tid):
    mailr = get_mailr_by(uid=uid, tid=tid)
    if not mailr:
        return False
    mailr.read()
    return True

def delete_topic(uid, tid):
    mailr = get_mailr_by(uid=uid, tid=tid)
    if not mailr:
        return
    mailr.delete()

def get_mailrs(uid, tid):
    sender = get_mailr_by(uid=uid, tid=tid)
    receiver = get_mailr_by(uid=sender.contact, tid=tid)
    return sender, receiver

def topic_notify(uid):
    return get_mailr_by(uid=uid, has_new=1)

def get_mailr_by(**kw):
    return Mailr.query.filter_by(**kw).first()

def get_topic(tid):
    return Topic.query.get(tid)

def get_reply(rid):
    return Reply.query.get(rid)
