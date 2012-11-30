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
        get_topic, get_user_replies, delete_reply, \
        delete_topic, create_topic, create_reply
from query.account import get_user

logger = logging.getLogger(__name__)
topic = Blueprint('topic', __name__)

@topic.route('/')
@topic.route('/<int:page>')
@login_required(next='account.login')
def index(page=1):
    list_page = get_user_topics(1, page)
    output = ''
    for topic in format_topic_list(list_page.items):
        output += '%s %s %s<br />' % (topic.title, topic.user.name, topic.last_reply.content)
    return output

@topic.route('/view/<int:topic_id>/')
@topic.route('/view/<int:topic_id>/<int:page>/')
@login_required(next='account.login')
def view(topic_id, page=1):
    topic = get_topic(topic_id)
    t = 'from' if topic.from_uid == g.current_user.id else 'to'
    list_page = get_user_replies(topic_id, page, t)
    output = ''
    for reply in format_reply_list(list_page.items):
        o = '%s %s %s<br />' % (reply.user.name, reply.time, reply.content)
        output = o + output
    return output

@csrf_exempt
@topic.route('/create/', methods=['GET', 'POST'])
@check_ua
@login_required(next='account.login')
def topic_create():
    if request.method == 'GET':
        return render_template('topic.create.html')

    to_uid = request.form.get('to_uid')
    title = request.form.get('title')
    content = request.form.get('content')
    who = get_user(to_uid)

    if not who:
        return '丫的你坑我呢'
    create_topic(g.current_user.id, to_uid, title, content)
    return 'ok'

@csrf_exempt
@topic.route('/reply/', methods=['GET', 'POST'])
@check_ua
@login_required(next='account.login')
def reply_create():
    if request.method == 'GET':
        return render_template('topic.reply.html')

    tid = request.form.get('tid')
    content = request.form.get('content')
    topic = get_topic(tid)
    if not topic:
        return '丫的你坑我呢'
    create_reply(g.current_user.id, topic, content)
    return 'ok'

def reply_delete(topic_id, reply_id):
    topic = get_topic(topic_id)
    t = 'from' if topic.from_uid == g.current_user.id else 'to'
    delete_reply(reply_id, t)
    return 'ok'

def topic_delete(topic_id):
    topic = get_topic(topic_id)
    t = 'from' if topic.from_uid == g.current_user.id else 'to'
    delete_topic(topic_id, t)
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
        topic = Obj()
        if item.from_uid != g.current_user.id:
            #means someone open topic with me
            topic.user = get_user(item.from_uid)
        else:
            #means I open topic with other
            topic.user = get_user(item.to_uid)
        topic.last_reply = get_reply(item.last_rid)
        topic.title = item.title
        yield topic

