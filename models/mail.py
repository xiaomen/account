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
    from_uid = db.Column(db.Integer, index=True)
    to_uid = db.Column(db.Integer, index=True)
    title = db.Column(db.String(45))
    content = db.Column(db.Text)
    is_read = db.Column(db.Integer, default=False, index=True)
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
    def create(from_uid, to_uid, title, content):
        mail = Mail(from_uid=from_uid,
                    to_uid = to_uid,
                    title = title,
                    content = content,
                    time = "%s" % datetime.now(),
                    is_read = False)
        db.session.add(mail)
        db.session.commit()

    @staticmethod
    def mark_as_read(mail):
        mail.is_read = True
        db.session.add(mail)
        db.session.commit()

