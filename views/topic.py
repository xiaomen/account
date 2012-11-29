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
    print get_user_topics(1, 1)
    return 'ok'
