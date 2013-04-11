# -*- coding: utf-8 -*-

import logging

from flask.views import MethodView
from flask import abort, request, Blueprint
from flaskext.csrf import csrf_exempt

from utils.weixin import Message, compute_signature, \
        return_message, check_keys, Robot

logger = logging.getLogger(__name__)
weixin = Blueprint('weixin', __name__)

class WeiXin(MethodView):
    def __init__(self):
        self.robot = Robot()
        super(WeiXin, self).__init__()

    def get(self):
        args = request.args.items()
        check_keys(args, ["signature", "timestamp", "nonce", "echostr"])
        signature = compute_signature(args.copy())
        if signature != args['signature']:
            logging.warning("Sigature error. %s", signature)
            raise abort(400)
        return args['echostr']

    def post(self):
        msg = Message(request.data)
        msg_splited = msg.Body.split(' ', 1)
        if len(msg_splited) < 2:
            msg_splited.append(' ')
        command, body = msg_splited
        command = command.lower()
        if command == "-code":
            command == "bind"
        robot = getattr(self.robot, command, None)
        if not robot:
            return return_message(msg.To, msg.From, '命令无法识别')
        return return_message(msg.To, msg.From, robot(body, msg))

weixin_view = WeiXin.as_view('weixin')
weixin.add_url_rule('/', view_func=weixin_view, methods=['GET'])
weixin.add_url_rule('/', view_func=csrf_exempt(weixin_view), methods=['POST'])

