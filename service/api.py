#!/usr/local/bin/python2.7
#coding:utf-8

# TODO init Flask environment
import app
import logging
from utils import get_user, get_unread_mail_count

logger = logging.getLogger(__name__)

def unread(uid):
    num = get_unread_mail_count(int(uid))
    return num

def people(uid):
    people = get_user(uid)
    if people:
        return dict(name=people.name, uid=people.id, domain=people.domain)
    return

