# -*- coding: utf-8 -*-

import logging

from flask import abort
from flask import request
from flask import Blueprint
from flaskext.csrf import csrf_exempt

from utils.weixin import Message, compute_signature, \
        return_message, check_code, check_keys

logger = logging.getLogger(__name__)

weixin = Blueprint('weixin', __name__)

@weixin.route('/', methods=["GET"])
def check_valid():
    args = dict(request.args.items())
    check_keys(args, ["signature", "timestamp", "nonce", "echostr"])
    signature = compute_signature(args.copy())
    if signature != args['signature']:
        logging.warning("Sigature error. %s", signature)
        raise abort(400)
    return args['echostr']

@csrf_exempt
@weixin.route('/', methods=["POST"])
def receive_msg():
    msg = Message(request.data)
    msg_splited = msg.Body.split(" ")
    if msg_splited[0] == "-code":
        if len(msg_splited) == 2:
            return return_message(msg.To, msg.From, check_code(msg_splited[1], msg))
        else:
            return return_message(msg.To, msg.From, "绑定失败，请检查验证码格式。")
    return ""
