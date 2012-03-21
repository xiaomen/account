#!/usr/bin/python
# encoding: UTF-8

__all__ = ['db', 'OAuth', 'User', 'Forget', 'init_db', 'create_token']

import hashlib
from random import choice
from datetime import datetime
from flaskext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()
def init_db(app):
    db.init_app(app)
    db.app = app
    db.create_all()

def create_token(length=16):
    chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    salt = ''.join([choice(chars) for i in range(length)])
    return salt

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.CHAR(16), nullable=False)
    passwd = db.Column(db.CHAR(50), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    avatar = db.Column(db.String(255))
    token = db.Column(db.CHAR(16))
    domain = db.Column(db.String(10), unique=True)

    def __init__(self, username, password, email, *args, **kwargs):
        self.name = username
        self.passwd = User.create_password(password)
        self.email = email.lower()
        self.token = create_token(16)
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @staticmethod
    def create_password(raw):
        salt = create_token(8)
        hsh = hashlib.sha1(salt + raw).hexdigest()
        return "%s$%s" % (salt, hsh)

    def check_password(self, raw):
        if '$' not in self.passwd:
            return False
        salt, hsh = self.passwd.split('$')
        verify = hashlib.sha1(salt + raw).hexdigest()
        return verify == hsh

class OAuth(db.Model):
    __tablename__ = 'oauth'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column('uid', db.Integer, nullable=False, unique=True)
    oauth_type = db.Column(db.String(20))
    oauth_uid = db.Column(db.String(200))
    oauth_token = db.Column(db.String(200))

    def __init__(self, uid, ouid, otype, *args, **kwargs):
        self.uid = uid
        self.oauth_uid = ouid
        self.oauth_type = otype
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def bind(self, uid):
        self.uid = uid

class Forget(db.Model):
    __tablename__ = 'forget'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column('uid', db.Integer, nullable=False, unique=True)
    stub = db.Column('stub', db.CHAR(20), nullable=False, unique=True)
    created = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, uid, stub):
        self.uid = uid
        self.stub = stub

