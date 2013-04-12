#!/usr/local/bin/python2.7
#coding:utf-8

from utils.token import get_uid
from query.account import get_user, clear_user_cache

class Robot(object):
    def __init__(self):
        self._commands = []
        commands = dir(self)
        for command in commands:
            if command.startswith('_'):
                continue
            self._commands.append(command)

    def bind(self, body, message):
        '''绑定校门口账号, 格式为「-code TOKEN」或者是「bind TOKEN」'''
        user = get_uid(body)
        if not user:
            return "绑定失败，请检查验证码或者返回绑定页面刷新获取新的验证码。"
        u = get_user(user)
        if not u:
            return "绑定失败，请检查验证码或者返回绑定页面刷新获取新的验证码。"
        u.set_weixin(message.From)
        clear_user_cache(u)
        return "绑定成功！"

    def unbind(self, body, message):
        '''undefine'''
        pass

    def who(self, body, message):
        '''undefine'''
        pass

    def repeat(self, body, message):
        '''Repeat what u say'''
        return body

    def help(self, command, message):
        '''显示可用命令，例如「help」，或者是「help bind」'''
        if not command.strip():
            return ' '.join(self._commands)
        if command not in self._commands:
            return '没有这个命令哦'
        else:
            return getattr(self, command).__doc__
