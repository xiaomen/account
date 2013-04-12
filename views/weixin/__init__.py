# -*- coding: utf-8 -*-


from flask import Blueprint
from flaskext.csrf import csrf_exempt

from views.weixin.weixin import WeiXin

weixin = Blueprint('weixin', __name__)

weixin_view = WeiXin.as_view('weixin')
weixin.add_url_rule('/', view_func=weixin_view, methods=['GET'])
weixin.add_url_rule('/', view_func=csrf_exempt(weixin_view), methods=['POST'])

