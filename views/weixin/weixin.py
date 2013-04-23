#!/usr/local/bin/python2.7
#coding:utf-8

import logging

from flask import abort, request
from flask.views import MethodView

from views.weixin.robot import Robot
from views.weixin.message import Message
from views.weixin.tools import compute_signature, \
        return_message, check_keys, parse_body

logger = logging.getLogger(__name__)

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
        command, body = parse_body(msg.Body)
        command = self.process_command(command)
        if not command in self.robot._commands:
            return ''
        handle = getattr(self.robot, command)
        return return_message(msg.To, msg.From, handle(body, msg))

    def process_command(self, command):
        ret = command.lower()
        if ret == "-code":
            ret == "bind"
        if isinstance(ret, unicode):
            ret = ret.encode('utf8')
        logger.info('command %s ' % ret)
        return ret

