#!/usr/bin/python
# encoding: UTF-8

__all__ = ['db_session', 'OAuth', 'User', 'init_db']

import config
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# setup sqlalchemy
engine = create_engine(config.DATABASE_URI)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    Base.metadata.create_all(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column(String(16))
    passwd = Column(String(200))
    email = Column(String(30))
    avatar = Column(String(255))

    def __init__(self, username, password, email, *args, **kwargs):
        self.name = username
        self.passwd = password
        self.email = email
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

class OAuth(Base):
    __tablename__ = 'oauth'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    uid = Column('uid', Integer)
    oauth_type = Column(String(20))
    oauth_uid = Column(String(200))
    oauth_token = Column(String(200))
    oauth_secret = Column(String(200))

    def __init__(self, uid, ouid, otype, *args, **kwargs):
        self.uid = uid
        self.oauth_uid = ouid
        self.oauth_type = otype
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

