# -*- coding: utf-8 -*-

import time
import logging
import hashlib
from lxml import etree
from pyquery import PyQuery as pq
from flask import abort

from config import WEIXIN_TOKEN

from utils.token import get_uid

from query.account import get_user

class Message(object):
    def __init__(self, data):
        self.t = pq(etree.fromstring(data), parser = "xml")
        self.To = self.t("ToUserName").text()
        self.From = self.t("FromUserName").text()
        self.Type = self.t("MsgType").text()
        self.Body = self.t("Content").text().strip()

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

def check_code(code, message):
    user = get_uid(code)
    if not user:
        return "绑定失败，请检查验证码或者返回绑定页面刷新获取新的验证码。"
    u = get_user(user) 
    if not u:
        return "绑定失败，请检查验证码或者返回绑定页面刷新获取新的验证码。"
    u.set_weixin(message.From)
    return "绑定成功，已绑定至帐号： %s" % u.name
