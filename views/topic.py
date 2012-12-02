#!/usr/local/bin/python2.7
#coding:utf-8

'''
send a reply, delete topic.reply_count cache, refresh topic list

'''

import logging
from flask import Blueprint, g, request
from flaskext.csrf import csrf_exempt

from utils.helper import Obj
from utils.account import login_required
from utils.ua import check_ua, render_template

from query.topic import get_user_topics, get_reply, \
        get_topic, get_user_replies, delete_topic, \
        make_topic, make_reply
from query.account import get_user

logger = logging.getLogger(__name__)
topic = Blueprint('topic', __name__)

@topic.route('/')
@topic.route('/<int:page>')
@login_required(next='account.login')
def index(page=1):
    list_page = get_user_topics(g.current_user.id, page)
    output = ''
    for topic in format_topic_list(list_page.items):
        output += '%s %s %s' % (topic.title, topic.user.name, topic.last_reply.content)
        if topic.has_new:
            output += 'new'
        output += '<br />'
    return output

@topic.route('/view/<int:topic_id>/')
@topic.route('/view/<int:topic_id>/<int:page>/')
@login_required(next='account.login')
def view(topic_id, page=1):
    topic = get_topic(topic_id)
    if not topic:
        return '你玩我呢！？'
    list_page = get_user_replies(topic_id, page)
    output = ''
    for reply in format_reply_list(list_page.items):
        o = '%s %s %s<br />' % (reply.user.name, reply.time, reply.content)
        output = o + output
    return output

@csrf_exempt
@topic.route('/create/<int:uid>/', methods=['GET', 'POST'])
@check_ua
@login_required(next='account.login')
def topic_create(uid):
    if request.method == 'GET':
        return render_template('topic.create.html', uid=uid)

    to_uid = request.form.get('to_uid')
    title = request.form.get('title')
    content = request.form.get('content')
    who = get_user(to_uid)

    if not who:
        return '丫的你坑我呢'
    make_topic(g.current_user.id, to_uid, title, content)
    return 'ok'

@csrf_exempt
@topic.route('/reply/<int:tid>/', methods=['GET', 'POST'])
@check_ua
@login_required(next='account.login')
def reply_create(tid):
    if request.method == 'GET':
        return render_template('topic.reply.html', tid=tid)

    tid = request.form.get('tid')
    content = request.form.get('content')
    topic = get_topic(tid)
    if not topic:
        return '丫的你坑我呢'
    make_reply(g.current_user.id, topic, content)
    return 'ok'

def topic_delete(topic_id):
    topic = get_topic(topic_id)
    if not topic:
        return 'failed'
    delete_topic(g.current_user.id, topic.id)
    return 'ok'

def format_reply_list(items):
    for item in items:
        reply = Obj()
        if item.who != g.current_user.id:
            reply.user = get_user(item.who)
        else:
            reply.user = g.current_user
        reply.content = item.content
        reply.time = item.time
        yield reply

def format_topic_list(items):
    for item in items:
        t = get_topic(item.tid)
        if not t:
            #TODO have to log
            continue
        topic = Obj()
        topic.user = get_user(item.contact)
        topic.last_reply = get_reply(t.last_rid)
        topic.title = t.title
        topic.has_new = item.has_new
        yield topic

