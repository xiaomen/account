#!/usr/local/bin/python2.7
#coding:utf-8

# TODO init Flask environment
import app
import logging
from query.account import get_user
from query.topic import topic_notify

logger = logging.getLogger(__name__)

def unread(uid):
    has = topic_notify(int(uid))
    return has

def people(uid):
    people = get_user(uid)
    if people:
        return dict(name=people.name, uid=people.id, domain=people.domain, avatar=people.avatar)
    return

