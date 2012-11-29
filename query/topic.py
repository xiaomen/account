#!/usr/local/bin/python2.7
#coding:utf-8

from sqlalchemy import or_
from sqlalchemy.sql.expression import desc

from config import PAGE_NUM
from models.topic import Topic, Reply

def get_user_topics(uid, page):
    page_obj = Topic.query.filter(or_(Topic.from_uid==uid, Topic.to_uid==uid))
    page_obj = page_obj.order_by(desc(Topic.last_time))
    page_obj = page_obj.paginate(page, per_page=PAGE_NUM)
    return page_obj
