#!/usr/local/bin/python2.7
#coding:utf-8

'''
send a reply, delete topic.reply_count cache, refresh topic list

'''

import logging
from flask import Blueprint, g, request, \
        url_for, redirect
from flaskext.csrf import csrf_exempt

from utils.helper import Obj
from utils.account import login_required
from utils.ua import check_ua, render_template

from query.topic import get_user_topics, get_reply, \
        get_topic, get_user_replies, delete_topic, \
        make_topic, make_reply, mark_read
from query.account import get_user

logger = logging.getLogger(__name__)
topic = Blueprint('topic', __name__)

@topic.route('/')
@topic.route('/<int:page>')
@login_required(next='account.login')
def index(page=1):
    msg = request.args.get('msg', None)
    list_page = get_user_topics(g.current_user.id, page)
    return render_template('topic.index.html', msg=msg, \
            topics=format_topic_list(list_page.items))

@topic.route('/view/<int:tid>/')
@topic.route('/view/<int:tid>/<int:page>/')
@login_required(next='account.login')
def view(tid, page=1):
    topic = get_topic(tid)
    if not topic:
        return redirect(url_for('topic.index'))
    mark_read(g.current_user.id, tid)
    list_page = get_user_replies(tid, page)
    return render_template('topic.view.html', \
            replies=format_reply_list(list_page.items), topic=topic)

@csrf_exempt
@topic.route('/create/<int:uid>/', methods=['GET', 'POST'])
@check_ua
@login_required(next='account.login')
def create_topic(uid):
    if request.method == 'GET':
        return render_template('topic.create.html', uid=uid)

    to_uid = request.form.get('to_uid')
    title = request.form.get('title')
    content = request.form.get('content')
    who = get_user(to_uid)

    if not who:
        #TODO return error code
        return render_template('topic.create.html', uid=uid)
    make_topic(g.current_user.id, to_uid, title, content)
    return redirect(url_for('topic.index'))

@csrf_exempt
@topic.route('/reply/<int:tid>/', methods=['GET', 'POST'])
@check_ua
@login_required(next='account.login')
def create_reply(tid):
    if request.method == 'GET':
        return render_template('topic.reply.html', tid=tid)

    tid = request.form.get('tid')
    content = request.form.get('content')
    topic = get_topic(tid)
    if topic:
        make_reply(g.current_user.id, topic, content)
    return redirect(url_for('topic.view', tid=tid))

def topic_delete(tid):
    topic = get_topic(tid)
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
        topic.id = t.id
        topic.user = get_user(item.contact)
        topic.last_reply = get_reply(t.last_rid)
        topic.title = t.title
        topic.has_new = item.has_new
        yield topic

