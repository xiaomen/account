#!/usr/bin/python
# encoding: UTF-8

from views.oauth.lib.qq import qq
from views.oauth.lib.weibo import weibo
from views.oauth.lib.douban import douban
from views.oauth.lib.renren import renren

from views.oauth.base import Base_OAuth_Login
from views.oauth.oauth import OAuth_views

qq_oauth_login = Base_OAuth_Login('qq', qq, 'openid')
weibo_oauth_login = Base_OAuth_Login('weibo', weibo, 'uid')
douban_oauth_login = Base_OAuth_Login('douban', douban, 'douban_user_id')
renren_oauth_login = Base_OAuth_Login('renren', renren, 'renren_uid')

oauth = OAuth_views()
oauth.add('qq', qq_oauth_login, qq)
oauth.add('weibo', weibo_oauth_login, weibo)
oauth.add('douban', douban_oauth_login, douban)
oauth.add('renren', renren_oauth_login, renren)

