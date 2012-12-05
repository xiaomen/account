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
from utils.helper import gen_list_page_obj
from models.topic import Topic, Reply, Mailr, create_topic, create_reply

from sheep.api.cache import cache

@cache('topic:list:{uid}:{page}', 86400)
def get_user_topics(uid, page):
    page_obj = Mailr.query.filter(and_(Mailr.uid==uid, Mailr.has_delete==0))
    page_obj = page_obj.order_by(desc(Mailr.last_time))
    page_obj = page_obj.paginate(page, per_page=PAGE_NUM)
    return gen_list_page_obj(page_obj)

@cache('topic:replies:{tid}:{page}', 86400)
def get_user_replies(tid, page):
    page_obj = Reply.query.filter(Reply.tid==tid)
    page_obj = page_obj.order_by(desc(Reply.time))
    page_obj = page_obj.paginate(page, per_page=PAGE_NUM)
    return gen_list_page_obj(page_obj)

@cache('topic:topic:{tid}', 86400)
def get_topic(tid):
    return Topic.query.get(tid)

#will not be delete or modify
@cache('topic:reply:{rid}', 864000)
def get_reply(rid):
    return Reply.query.get(rid)

@cache('topic:mailr:{uid}:{tid}', 86400)
def get_mailr(uid, tid):
    return Mailr.query.filter_by(uid=uid, tid=tid).first()

@cache('topic:notify:{uid}', 86400)
def topic_notify(uid):
    return bool(Mailr.query.filter_by(uid=uid, has_new=1).first())

def get_topic_reploy_count(tid):
    topic = get_topic(tid)
    count = topic.reply.count
    return count

def get_mailrs(uid, tid):
    sender = get_mailr(uid, tid)
    receiver = get_mailr(sender.contact, tid)
    return sender, receiver

def make_topic(uid, to_uid, title, content):
    #TODO clean cache!!!
    return create_topic(uid, to_uid, title, content)

def make_reply(sender, receiver, topic, content):
    return create_reply(sender, receiver, topic, content)

def mark_read(uid, tid):
    mailr = get_mailr(uid=uid, tid=tid)
    if not mailr:
        return False
    return mailr.read()

def delete_topic(mailr):
    mailr.delete()

