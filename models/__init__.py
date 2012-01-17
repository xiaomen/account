#!/usr/bin/python
# encoding: UTF-8

__all__ = ['db', 'OAuth', 'User', 'init_db']

import hashlib
from flaskext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(16))
    passwd = db.Column(db.String(200))
    email = db.Column(db.String(30))
    avatar = db.Column(db.String(255))

    def __init__(self, username, password, email, *args, **kwargs):
        self.name = username
        self.passwd = User.create_password(username, password)
        self.email = email
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @staticmethod
    def create_password(username, password):
        m = hashlib.sha1()
        m.update(username)
        p1 = m.hexdigest()
        p1 = p1[10:20] + p1[:10]
        m = hashlib.md5()
        m.update(p1)
        m.update(password)
        return m.hexdigest()

    def check_password(self, passwd):
        return self.passwd == User.create_password(self.name, passwd)

class OAuth(db.Model):
    __tablename__ = 'oauth'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column('uid', db.Integer)
    oauth_type = db.Column(db.String(20))
    oauth_uid = db.Column(db.String(200))
    oauth_token = db.Column(db.String(200))
    oauth_secret = db.Column(db.String(200))

    def __init__(self, uid, ouid, otype, *args, **kwargs):
        self.uid = uid
        self.oauth_uid = ouid
        self.oauth_type = otype
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def bind(self, uid):
        self.uid = uid

