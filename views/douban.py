#!/usr/bin/python
# encoding: UTF-8

from flask import Blueprint
from lib.douban import douban
from base import Base_OAuth_Login

douban_oauth = Blueprint('douban_oauth', __name__)
douban_oauth_login = Base_OAuth_Login('douban', douban, 'douban_user_id')

douban.tokengetter(douban_oauth_login.get_token)
douban_oauth.add_url_rule('/Login', view_func=douban_oauth_login.login)
douban_oauth.add_url_rule('/Authorized', view_func=douban.authorized_handler(douban_oauth_login.authorized))

