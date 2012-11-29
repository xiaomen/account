#!/usr/local/bin/python2.7
#coding:utf-8

import logging
from flask import Blueprint

from models.topic import Topic, Reply
from query.topic import get_user_topics

logger = logging.getLogger(__name__)
topic = Blueprint('topic', __name__)

@topic.route('/')
def test():
    list_page = get_user_topics(1, 1)
    return 'ok'

def format_topic_list(items):

    for item in items:
        if item.from_uid != uid:
            uids.append(item.from_uid)

