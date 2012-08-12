#!/usr/bin/env python
# -*- encoding: utf-8; indent-tabs-mode: nil -*-
#
# Copyright 2012 crackcell
#

from datetime import datetime

from sqlalchemy.sql.expression import desc
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
    time = db.Column(db.DateTime, default=datetime.now)
    is_show = db.Column(db.CHAR(3), default='1|1')

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

    @staticmethod
    def mark_as_read(mail):
        mail.is_read = True
        db.session.add(mail)
        db.session.commit()

    @staticmethod
    def delete_inbox(mail):
        show = mail.is_show
        mail.is_show = '0' + show[-2:]
        db.session.add(mail)
        db.session.commit()

    @staticmethod
    def delete_outbox(mail):
        show = mail.is_show
        mail.is_show = show[:-1] + '0'
        db.session.add(mail)
        db.session.commit()

    @staticmethod
    def get_inbox_page(uid, page, per_page):
        page_obj = Mail.query.filter(Mail.to_uid==uid).order_by(desc(Mail.time)).paginate(page, per_page=per_page)
        return page_obj

    @staticmethod
    def get_outbox_page(uid, page, per_page):
        page_obj = Mail.query.filter(Mail.from_uid==uid).order_by(desc(Mail.time)).paginate(page, per_page=per_page)
        return page_obj
