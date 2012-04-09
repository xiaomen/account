#!/usr/bin/env python
# -*- encoding: utf-8; indent-tabs-mode: nil -*-
#
# Copyright 2012 crackcell
#

from datetime import *

from flaskext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()
def init_mail_db(app):
    db.init_app(app)
    db.app = app
    db.create_all()

class Mail(db.Model):
    __tablename__ = 'mail'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    from_uid = db.Column(db.Integer)
    to_uid = db.Column(db.Integer)
    title = db.Column(db.String(45))
    content = db.Column(db.Text)
    is_read = db.Column(db.Integer)
    time = db.Column(db.DateTime)

    def __init__(self, from_uid, to_uid, title, content, is_read, time, *args, **kwargs):
        self.from_uid = from_uid
        self.to_uid = to_uid
        self.title = title
        self.content = content
        self.is_read = is_read
        self.time = time
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @staticmethod
    def get_recv_all(uid):
        return Mail.query.filter_by(to_uid=uid).all()

    @staticmethod
    def get_sent_all(uid):
        return Mail.query.filter_by(from_uid=uid).all()

    @staticmethod
    def insert(from_uid, to_uid, title, content):
        mail = Mail(from_uid=from_uid,
                    to_uid = to_uid,
                    title = title,
                    content = content,
                    time = "%s" % datetime.now(),
                    is_read = False)
        db.session.add(mail)
        db.session.commit()

class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer)
    unread = db.Column(db.Integer)

    def __init__(self, uid, unread, *args, **kwargs):
        self.uid = uid
        self.unread = unread
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
    @staticmethod
    def get_unread_mail_count(uid):
        notification = Notification.query.filter_by(uid=uid).first()
        if not notification:
            Notification.add_new_notification(uid)
            return 0
        return notification.unread

    @staticmethod
    def add_new_notification(uid):
        notification = Notification(uid=uid, unread=0)
        db.session.add(notification)
        db.session.commit()

    @staticmethod
    def increase_unread(uid):
        notification = Notification.query.filter_by(uid=uid).with_lockmode("update").one()
        notification.unread += 1
        db.session.commit()

    @staticmethod
    def decrease_unread(uid):
        notification = Notification.query.filter_by(uid=uid).with_lockmode("update").one()
        if notification.unread != 0:
            notification.unread -= 1
            db.session.commit()
