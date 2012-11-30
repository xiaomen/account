#!/usr/local/bin/python2.7
#coding:utf-8

'''
用户有多少topics应该是存在另外一张表里面，
后期优化应考虑topic分页的时候用多个查询代替count锁表。
比如，先查用户有多少个topic，然后从topic表中limit查对应topic。
同理适用于reply，先从topic表中查到reply_count再分页。
'''

from sqlalchemy import and_, or_
from sqlalchemy.sql.expression import desc

from config import PAGE_NUM
from models.topic import Topic, Reply

def get_user_topics(uid, page):
    page_obj = Topic.query.filter(or_(and_(Topic.from_uid==uid, Topic.from_show==1), and_(Topic.to_uid==uid, Topic.to_show==1)))
    page_obj = page_obj.order_by(desc(Topic.last_time))
    page_obj = page_obj.paginate(page, per_page=PAGE_NUM)
    return page_obj

def get_user_replies(tid, page, t='from'):
    page_obj = Reply.query.filter(Reply.tid==tid)
    page_obj = page_obj.filter(getattr(Reply, '%s_show' % t)==1)
    page_obj = page_obj.order_by(desc(Reply.time))
    page_obj = page_obj.paginate(page, per_page=PAGE_NUM)
    return page_obj

def create_topic(uid, to_uid, title, content):
    topic = Topic.create(uid, to_uid, title)
    create_reply(uid, topic, content)
    return topic

def create_reply(uid, topic, content):
    reply = Reply.create(topic.id, content, uid)
    topic.add_reply(reply)
    return reply

def delete_reply(rid, t='from'):
    reply = get_reply(rid)
    getattr(reply, '%s_delete' % t)()

def delete_topic(tid, t='from'):
    topic = get_topic(tid)
    getattr(topic, '%s_delete' % t)()

def get_topic(tid):
    return Topic.query.get(tid)

def get_reply(rid):
    return Reply.query.get(rid)
