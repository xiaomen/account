#!/usr/local/bin/python2.7
#coding:utf-8

import logging

from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy

logger = logging.getLogger('__name__')

db = SQLAlchemy()
def init_topic_db(app):
    db.init_app(app)
    db.app = app
    db.create_all()

class MailrMeta(db.Model):
    __tablename__ = 'mailr_meta'
    uid = db.Column('id', db.Integer, primary_key=True)
    topic_count = db.Column(db.Integer, nullable=False, default=0)
    last_time = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __init__(self, uid, topic_count, last_time):
        self.uid = uid
        self.topic_count = topic_count
        self.last_time = last_time

    @staticmethod
    def create(uid, topic_count, last_time):
        mailr_meta = MailrMeta(uid, topic_count, last_time)
        db.session.add(mailr_meta)
        db.session.commit()
        return mailr_meta

    def create_topic(self, last_time):
        self.topic_count = self.topic_count + 1
        self.last_time = last_time

    def create_reply(self, last_time, count=False):
        self.last_time = last_time
        if count:
            self.topic_count = self.topic_count + 1

    def delete(self):
        self.topic_count = self.topic_count - 1
        db.session.add(self)
        db.session.commit()

class Mailr(db.Model):
    __tablename__ = 'mailr'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer, index=True, nullable=False)
    tid = db.Column(db.Integer, index=True, nullable=False)
    contact = db.Column(db.Integer, nullable=False)
    last_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    has_new = db.Column(db.Integer, nullable=False, default=0)
    has_delete = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, uid, tid, **kwargs):
        self.uid = uid
        self.tid = tid
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @staticmethod
    def create(uid, tid, last_time, contact):
        mailr = Mailr(uid = uid,
                      tid = tid,
                      contact = contact,
                      last_time = last_time)
        db.session.add(mailr)
        db.session.commit()
        return mailr

    def new_message(self, last_time, has_new=0):
        if self.has_new != has_new:
            self.has_new = has_new
        if self.has_delete == 1:
            self.has_delete = 0
        self.last_time = last_time

    def delete(self):
        self.has_delete = 1
        db.session.add(self)
        db.session.commit()

    def read(self):
        if self.has_new:
            self.has_new = 0
            db.session.add(self)
            db.session.commit()
            return True
        return False

class Topic(db.Model):
    __tablename__ = 'topic'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(45), nullable=False)
    last_rid = db.Column(db.Integer, nullable=False, default=0)
    reply_count = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, title, **kwargs):
        self.title = title
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @staticmethod
    def create(title):
        topic = Topic(title = title)
        db.session.add(topic)
        db.session.commit()
        return topic

    def add_reply(self, reply):
        self.last_rid = reply.id
        self.reply_count = self.reply_count + 1

class Reply(db.Model):
    __tablename__ = 'reply'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    tid = db.Column(db.Integer, index=True, nullable=False)
    content = db.Column(db.Text)
    time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    who = db.Column(db.Integer, nullable=False)

    def __init__(self, tid, content, who):
        self.tid = tid
        self.content = content
        self.who = who
        self.time = datetime.now()

    @staticmethod
    def create(tid, content, who):
        reply = Reply(tid=tid, content=content, who=who)
        db.session.add(reply)
        db.session.commit()
        return reply

def create_topic(sender, receiver, title, content):
    try:
        topic = Topic(title=title)
        db.session.add(topic)
        db.session.flush()
        reply = Reply(topic.id, content, sender.uid)
        db.session.add(reply)
        db.session.flush()
        topic.add_reply(reply)
        db.session.add(topic)
        db.session.flush()
        mailr_sender = Mailr(sender.uid, topic.id, \
                      contact=receiver.uid, \
                      last_time=reply.time)
        mailr_receiver = Mailr(receiver.uid, topic.id, \
                         contact=sender.uid, \
                         last_time=reply.time, \
                         has_new=1)
        db.session.add(mailr_sender)
        db.session.add(mailr_receiver)
        sender.create_topic(reply.time)
        receiver.create_topic(reply.time)
        db.session.add(sender)
        db.session.add(receiver)
        db.session.commit()
        return topic
    except Exception:
        logger.exception('create topic failed')
        db.session.rollback()
    return None

def create_reply(sender, receiver, sender_meta, receiver_meta, topic, content):
    try:
        reply = Reply(topic.id, content, sender.uid)
        db.session.add(reply)
        db.session.flush()
        topic.add_reply(reply)
        sender_meta.create_reply(reply.time)
        sender.new_message(reply.time)
        if receiver.has_delete == 1:
            receiver_meta.create_reply(reply.time, count=True)
        else:
            receiver_meta.create_reply(reply.time)
        receiver.new_message(reply.time, has_new=1)
        db.session.add(topic)
        db.session.add(sender)
        db.session.add(receiver)
        db.session.add(sender_meta)
        db.session.add(receiver_meta)
        db.session.commit()
        return True
    except Exception:
        logger.exception('create reply failed')
        db.session.rollback()
    return False

