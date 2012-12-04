#!/usr/bin/env python
# -*- encoding: utf-8; indent-tabs-mode: nil -*-
#
# Copyright 2012 crackcell
#

from datetime import datetime

from sqlalchemy.sql.expression import desc
from flask.ext.sqlalchemy import SQLAlchemy

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
    time = db.Column(db.DateTime, default=datetime.now)
    inbox = db.Column(db.Integer, default=1)
    outbox = db.Column(db.Integer, default=1)

    def __init__(self, from_uid, to_uid, title, content, is_read, *args, **kwargs):
        self.from_uid = from_uid
        self.to_uid = to_uid
        self.title = title
        self.content = content
        self.is_read = is_read
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @staticmethod
    def create(from_uid, to_uid, title, content):
        mail = Mail(from_uid=from_uid,
                    to_uid = to_uid,
                    title = title,
                    content = content,
                    is_read = False)
        db.session.add(mail)
        db.session.commit()

    def mark_as_read(self):
        self.is_read = True
        db.session.add(self)
        db.session.commit()

    def delete_inbox(self):
        self.inbox = 0
        db.session.add(self)
        db.session.commit()

    def delete_outbox(self):
        self.outbox = 0
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_inbox_page(uid, page, per_page):
        page_obj = Mail.query.filter(Mail.to_uid==uid).filter(Mail.inbox==1).order_by(desc(Mail.time)).paginate(page, per_page=per_page)
        return page_obj

    @staticmethod
    def get_outbox_page(uid, page, per_page):
        page_obj = Mail.query.filter(Mail.from_uid==uid).filter(Mail.outbox==1).order_by(desc(Mail.time)).paginate(page, per_page=per_page)
        return page_obj
