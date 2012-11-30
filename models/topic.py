#!/usr/local/bin/python2.7
#coding:utf-8

from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()
def init_topic_db(app):
    db.init_app(app)
    db.app = app
    db.create_all()

class Topic(db.Model):
    __tablename__ = 'topic'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(45), nullable=False)
    from_uid = db.Column(db.Integer, index=True, nullable=False)
    to_uid = db.Column(db.Integer, index=True, nullable=False)
    last_rid = db.Column(db.Integer, nullable=False, default=0)
    reply_count = db.Column(db.Integer, nullable=False, default=0)
    last_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    from_show = db.Column(db.Integer, nullable=False, default=1)
    to_show = db.Column(db.Integer, nullable=False, default=1)

    def __init__(self, title, from_uid, to_uid, **kwargs):
        self.title = title
        self.from_uid = from_uid
        self.to_uid = to_uid
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @staticmethod
    def create(from_uid, to_uid, title):
        topic = Topic(from_uid=from_uid,
                      to_uid = to_uid,
                      title = title)
        db.session.add(topic)
        db.session.commit()
        return topic

    def add_reply(self, reply):
        self.last_rid = reply.id
        self.reply_count = self.reply_count + 1
        self.last_time = datetime.now()
        db.session.add(self)
        db.session.commit()

    def from_delete(self):
        self.from_show = 0
        db.session.add(self)
        db.session.commit()

    def to_delete(self):
        self.delete_show = 0
        db.session.add(self)
        db.session.commit()

    def activate(self):
        f = False
        if self.from_show == 0:
            self.from_show == 1
            f = True
        if self.to_show == 0:
            self.to_show == 1
            f = True
        if f:
            db.session.add(self)
            db.session.commit()

class Reply(db.Model):
    __tablename__ = 'reply'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    tid = db.Column(db.Integer, index=True, nullable=False)
    content = db.Column(db.Text)
    time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    who = db.Column(db.Integer, nullable=False)
    from_show = db.Column(db.Integer, nullable=False, default=1)
    to_show = db.Column(db.Integer, nullable=False, default=1)

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

    def from_delete(self):
        self.from_show = 0
        db.session.add(self)
        db.session.commit()

    def to_delete(self):
        self.to_show = 0
        db.session.add(self)
        db.session.commit()

