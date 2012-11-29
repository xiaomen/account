#!/usr/local/bin/python2.7
#coding:utf-8

'''
send a reply, delete topic.reply_count cache, refresh topic list

'''

import logging
from flask import Blueprint, g

from utils.helper import Obj
from models.topic import Topic, Reply
from query.topic import get_user_topics, get_reply
from query.account import get_user

logger = logging.getLogger(__name__)
topic = Blueprint('topic', __name__)

@topic.route('/')
def test():
    list_page = get_user_topics(1, 1)
    output = ''
    for topic in format_topic_list(list_page.items):
        output += '%s %s %s<br />' % (topic.title, topic.user.name, topic.last_reply.content)
    return output

def format_topic_list(items):
    for item in items:
        topic = Obj()
        if item.from_uid != g.current_user.id:
            #means someone open topic with me
            topic.user = get_user(item.from_uid)
        else:
            #means I open topic with other
            topic.user = get_user(item.to_uid)
        topic.last_reply = get_reply(item.last_rid)
        topic.title = item.title
        yield topic

