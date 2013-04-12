#!/usr/local/bin/python2.7
#coding:utf-8

from flask import g

from utils.helper import Obj
from sheep.api.cache import backend, cross_cache

from query.account import get_user
from query.topic import get_reply, get_topic

def clean_cache(uid, to_uid, tid):
    backend.delete('topic:topic:%d' % tid)
    backend.delete('topic:replies:%d:1' % tid)
    backend.delete('topic:list:%d:1' % uid)
    backend.delete('topic:list:%d:1' % to_uid)
    backend.delete('topic:notify:%d' % to_uid)
    backend.delete('topic:meta:%d' % uid)
    backend.delete('topic:meta:%d' % to_uid)
    cross_cache.delete('open:account:unread:{0}'.format(to_uid))

def format_reply_list(items):
    for item in items:
        reply = Obj()
        if item.who != g.current_user.id:
            reply.user = get_user(item.who)
        else:
            reply.user = g.current_user
        reply.content = item.content
        reply.time = item.time
        yield reply

def format_topic_list(items):
    for item in items:
        t = get_topic(item.tid)
        if not t:
            #TODO have to log
            continue
        topic = Obj()
        topic.id = t.id
        topic.user = get_user(item.contact)
        topic.last_reply = get_reply(t.last_rid)
        topic.title = t.title
        topic.has_new = item.has_new
        yield topic

