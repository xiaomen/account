#!/usr/local/bin/python2.7
#coding:utf-8

import datetime
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()
def init_mail_db(app):
    db.init_app(app)
    db.app = app
    db.create_all()

class Topic(db.Model):
    __tablename__ = 'topic'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(45), nullable=False)
    from_uid = db.Column(db.Integer, index=True, nullable=False)
    to_uid = db.Column(db.Integer, index=True, nullable=False)
    last_rid = db.Column(db.Integer, index=True, nullable=False)
    reply_count = db.Column(db.Integer, index=True, nullable=False, default=0)
    unread_count = db.Column(db.Integer, index=True, nullable=False, default=0)
    last_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())

    def __init__(self, title, from_uid, to_uid, last_rid, **kwargs):
        self.title = title
        self.from_uid = from_uid
        self.to_uid = to_uid
        self.last_rid = last_rid
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @staticmethod
    def create(from_uid, to_uid, title, last_rid):
        topic = Topic(from_uid=from_uid,
                    to_uid = to_uid,
                    title = title,
                    last_rid = last_rid,
                    unread_count = 1)
        db.session.add(topic)
        db.session.commit()

    def add_reply(self, reply):
        self.last_rid = reply.id
        self.reply_count = self.reply_count + 1
        self.unread_count = self.unread_count + 1
        self.last_time = datetime.datetime.now()

