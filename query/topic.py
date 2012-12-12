#!/usr/local/bin/python2.7
#coding:utf-8

'''
用户有多少topics应该是存在另外一张表里面，
后期优化应考虑topic分页的时候用多个查询代替count锁表。
比如，先查用户有多少个topic，然后从topic表中limit查对应topic。
同理适用于reply，先从topic表中查到reply_count再分页。
'''

from datetime import datetime
from sqlalchemy import and_
from flask_sqlalchemy import Pagination
from sqlalchemy.sql.expression import desc

from config import PAGE_NUM
from utils.helper import gen_list_page_obj
from models.topic import Topic, Reply, UserTopic, UserTopicMeta, \
        create_topic, create_reply

from sheep.api.cache import cache, backend

@cache('topic:list:{uid}:{page}', 86400)
def get_user_topics(uid, page):
    meta = get_user_topic_meta(uid)
    if not meta:
        meta = set_user_topic_meta(uid)
    page_obj = UserTopic.query.filter(and_(UserTopic.uid==uid, UserTopic.has_delete==0))
    page_obj = page_obj.order_by(desc(UserTopic.last_time))
    items = page_obj.limit(PAGE_NUM).offset((page - 1) * PAGE_NUM).all()
    page_obj = Pagination(page_obj, page, PAGE_NUM, meta.topic_count, items)
    ret = gen_list_page_obj(page_obj)
    ret.last_time = meta.last_time
    return ret

@cache('topic:replies:{tid}:{page}', 86400)
def get_user_replies(tid, page):
    topic = get_topic(tid)
    page_obj = Reply.query.filter(Reply.tid==tid)
    page_obj = page_obj.order_by(desc(Reply.time))
    items = page_obj.limit(PAGE_NUM).offset((page - 1) * PAGE_NUM).all()
    page_obj = Pagination(page_obj, page, PAGE_NUM, topic.reply_count, items)
    return gen_list_page_obj(page_obj)

@cache('topic:topic:{tid}', 86400)
def get_topic(tid):
    return Topic.query.get(tid)

#will not be delete or modify
@cache('topic:reply:{rid}', 864000)
def get_reply(rid):
    return Reply.query.get(rid)

@cache('topic:user_topic:{uid}:{tid}', 86400)
def get_user_topic(uid, tid):
    return UserTopic.query.filter_by(uid=uid, tid=tid).limit(1).first()

@cache('topic:notify:{uid}', 86400)
def topic_notify(uid):
    return bool(UserTopic.query.filter_by(uid=uid, has_new=1).first())

@cache('topic:user_topic_meta:{uid}', 86400)
def get_user_topic_meta(uid):
    meta = UserTopicMeta.query.get(uid)
    return meta

def set_user_topic_meta(uid):
    meta = UserTopicMeta.create(uid, 0, datetime.now())
    return meta

def get_topic_reploy_count(tid):
    topic = get_topic(tid)
    count = topic.reply.count
    return count

def get_topic_users(uid, tid):
    sender = get_user_topic(uid, tid)
    receiver = get_user_topic(sender.contact, tid)
    return sender, receiver

def make_topic(uid, to_uid, title, content):
    sender = get_user_topic_meta(uid)
    if not sender:
        sender = set_user_topic_meta(uid)
    receiver = get_user_topic_meta(to_uid)
    if not receiver:
        receiver = set_user_topic_meta(to_uid)
    return create_topic(sender, receiver, title, content)

def make_reply(sender, receiver, topic, content):
    sm = get_user_topic_meta(sender.uid)
    rm = get_user_topic_meta(receiver.uid)
    if not sm or not rm:
        #TODO 理论上这里一定有user_topic_meta
        raise Exception('what the hell!?')
    return create_reply(sender, receiver, sm, rm, topic, content)

def mark_read(uid, tid):
    user_topic = get_user_topic(uid=uid, tid=tid)
    if not user_topic:
        return False
    return user_topic.read()

def delete_topic(user_topic):
    user_topic_meta = get_user_topic_meta(user_topic.uid)
    if not user_topic_meta:
        #TODO 理论上这里一定有user_topic_meta
        raise Exception('what the hell!?')
    user_topic.delete()
    user_topic_meta.delete()

