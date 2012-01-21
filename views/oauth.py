#!/usr/bin/python
# encoding: UTF-8

from flask import Blueprint
from lib.qq import qq
from lib.weibo import weibo
from lib.douban import douban
from lib.renren import renren
from base import Base_OAuth_Login

qq_oauth_login = Base_OAuth_Login('qq', qq, 'openid')
weibo_oauth_login = Base_OAuth_Login('weibo', weibo, 'uid')
douban_oauth_login = Base_OAuth_Login('douban', douban, 'douban_user_id')
renren_oauth_login = Base_OAuth_Login('renren', renren, 'renren_uid')

class OAuth_views(object):
    def __init__(self):
        self.views = {}

    def add(self, oauth_name, login_obj, oauth_obj):
        self.views[oauth_name] = Blueprint('%s_oauth' % oauth_name, __name__)
        self._init_tokengetter(login_obj, oauth_obj)
        self._init_url_rule(oauth_name, login_obj, oauth_obj)

    def _init_url_rule(self, oauth_name, login_obj, oauth_obj):
        blueprint = self.views.get(oauth_name, None)
        if not blueprint:
            return
        blueprint.add_url_rule('/login', view_func=getattr(login_obj, 'login'))
        blueprint.add_url_rule('/authorized', view_func=\
            getattr(oauth_obj, 'authorized_handler')(getattr(login_obj, 'authorized'))
        )

    def _init_tokengetter(self, login_obj, oauth_obj):
        getattr(oauth_obj, 'tokengetter')(getattr(login_obj, 'get_token'))

    def register_blueprints(self, app):
        for name, blueprint in self.views.iteritems():
            url_prefix = '/%s' % name
            app.register_blueprint(blueprint, url_prefix=url_prefix)

views = OAuth_views()
views.add('qq', qq_oauth_login, qq)
views.add('weibo', weibo_oauth_login, weibo)
views.add('douban', douban_oauth_login, douban)
views.add('renren', renren_oauth_login, renren)
