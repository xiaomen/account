#!/usr/bin/python
# encoding: UTF-8

__all__ = ['db_session', 'User', 'init_db']

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
    uid = Column(String(200))
    oauth_token = Column(String(200))
    oauth_secret = Column(String(200))

    def __init__(self, uid, *args, **kwargs):
        self.uid = uid
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
