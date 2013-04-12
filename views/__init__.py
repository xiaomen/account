#!/usr/bin/python
# encoding: UTF-8

from views.oauth import oauth
from views.topic import topic
from views.people import people
from views.weixin import weixin
from views.account import account

def init_views(app):
    oauth.register_blueprints(app)
    app.register_blueprint(account, url_prefix='/account')
    app.register_blueprint(people, url_prefix='/people')
    app.register_blueprint(topic, url_prefix='/mail')
    app.register_blueprint(weixin, url_prefix='/wx')
