#!/usr/local/bin/python2.7
#coding:utf-8

from sheep.api.service import get_service
from views.weixin.tools import parse_body
from utils.token import get_uid
from query.account import get_user, get_user_by_weixin, \
        clear_user_cache

JOB_SVC_NAME = 'service.api'
#TODO use tcp proxy
JOB_SVC_PATH = '/data/run/sheep-job.sock'

class BaseRobot(object):
    def __init__(self):
        self._commands = []
        commands = dir(self)
        for command in commands:
            if command.startswith('_'):
                continue
            self._commands.append(command)

    def help(self, command, message):
        '''显示可用命令，例如「help」，或者是「help bind」'''
        if not command.strip():
            return ' '.join(self._commands)
        if command not in self._commands:
            return '没有这个命令哦'
        else:
            ret = getattr(self, command).__doc__
            if not ret:
                return '其实我也不知道这是作甚的'
            return ret

class Robot(BaseRobot):
    def __init__(self):
        super(Robot, self).__init__()
        self.jobrobot = JobRobot()

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
        '''解除校门口账号绑定'''
        user = get_user_by_weixin(message.From)
        if not user:
            return '似乎你之前并未绑定过哦'
        user.remove_weixin()
        clear_user_cache(user)
        return '解除绑定成功'

    def who(self, body, message):
        '''我是谁'''
        user = get_user_by_weixin(message.From)
        if not user:
            return '你存在么'
        return 'email: %s' % user.email

    def job(self, body, message):
        sub_command, sub_body = parse_body(body)
        if not sub_command in self.jobrobot._commands:
            return '机器人不知道你想干嘛哦~'
        handle = getattr(self.jobrobot, sub_command)
        return handle(sub_body, message)

    def repeat(self, body, message):
        '''Repeat what u say'''
        return body

class JobRobot(BaseRobot):
    def __init__(self):
        super(JobRobot, self).__init__()
        self.job = get_service('service.api', unix=JOB_SVC_PATH)

    def list(self, body, message):
        '''列出最新工作，通过「job list 2」来翻页或者「job list 中南 2」来筛选学校并翻页哦'''
        user = get_user_by_weixin(message.From)
        sp = body.split(' ', 1)
        page = 1
        fid = None
        if sp and len(sp) == 1:
            s = sp[0]
            if s.isdigit():
                page = int(s)
            else:
                fid = s
        elif sp and len(sp) >= 2:
            fid, page = sp[:2]
        else:
            return '命令不正确哦~请用job help list查看如何使用'
        try:
            page = int(page)
            if fid:
                fid = int(fid)
        except Exception:
            page = 1
            fid = None
        ret = self.job.list_jobs(user.id, page, fid)
        if not ret:
            return '没有了哦'
        items = ['把-id之后的数字组合成命令「job detail 1234」则可以看到详细信息\n']
        for item in ret['rs']:
            items.append('-id %d\n%s\n%s\n在 %s\n' % (item['aid'], item['title'], \
                    item['date'], item['place']))
        return '-----------------------\n'.join(items)

    def interns(self, body, message):
        pass

    def collect(self, body, message):
        pass

    def favorite(self, body, message):
        pass

    def detail(self, body, message):
        '''显示工作详细信息，通过「job detail 1234」来查看'''
        sp = body.split(' ', 1)
        user = get_user_by_weixin(message.From)
        if sp and len(sp) == 1 and sp[0].isdigit():
            aid = int(sp[0])
        else:
            return '这不是合法的工作id哦'
        ret = self.job.detail(user.id, aid)
        if not ret:
            return '找不到这个工作的详细信息哦'
        return '学校: %s\n时间: %s\n地点: %s\n详细: %s' % (ret['feed'], ret['date'], ret['place'], ret['url'])

