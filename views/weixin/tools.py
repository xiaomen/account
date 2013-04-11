# -*- coding: utf-8 -*-

import time
import logging
import hashlib
from flask import abort

from config import WEIXIN_TOKEN

def return_message(fromUser, toUser, content):
    return """<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%d</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[%s]]></Content>
<FuncFlag>0</FuncFlag>
</xml>""" % (toUser, fromUser, int(time.time()), content)

def compute_signature(args):
    sign_args = [args['timestamp'], args['nonce'], WEIXIN_TOKEN]
    sign_args.sort()
    return hashlib.sha1("".join(sign_args)).hexdigest()

def check_keys(src, keys):
    for key in keys:
        if key not in src:
            logging.warning("missing %s", key)
            raise abort(400)

