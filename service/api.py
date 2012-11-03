#!/usr/local/bin/python2.7
#coding:utf-8

import logging
from utils import get_user, get_unread_mail_count

logger = logging.getLogger(__name__)

def unread(id):
    num = get_unread_mail_count(int(id))
    return num

def people(username):
    people = get_user(username)
    if people:
        return dict(name=people.name, uid=people.id, domain=people.domain)
    return

