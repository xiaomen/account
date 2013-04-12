#!/usr/local/bin/python2.7
#coding:utf-8

import logging

from flask import abort, request
from flask.views import MethodView

from views.weixin.robot import Robot
from views.weixin.message import Message
from views.weixin.tools import compute_signature, \
        return_message, check_keys

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
        msg_splited = msg.Body.split(' ', 1)
        if len(msg_splited) < 2:
            msg_splited.append(' ')
        command, body = msg_splited
        command = self.process_command(command)
        if not command in self.robot._commands:
            return return_message(msg.To, msg.From, '命令无法识别')
        robot = getattr(self.robot, command)
        return return_message(msg.To, msg.From, robot(body, msg))

    def process_command(self, command):
        ret = command.lower()
        if ret == "-code":
            ret == "bind"
        if isinstance(ret, unicode):
            ret = ret.encode('utf8')
        logger.info('command %s ' % ret)
        return ret

