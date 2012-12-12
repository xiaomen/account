#!/usr/local/bin/python2.7
#coding:utf-8

'''
send a reply, delete topic.reply_count cache, refresh topic list

'''

import logging
from flask import Blueprint, g, request, \
        url_for, redirect, abort
from flaskext.csrf import csrf_exempt

from utils.helper import Obj
from utils.account import login_required
from utils.ua import check_ua, render_template

from query.topic import get_user_topics, get_reply, \
        get_topic, get_user_replies, delete_topic, \
        make_topic, make_reply, mark_read, \
        get_user_topics, get_user_topic
from query.account import get_user

from sheep.api.cache import backend, cross_cache

logger = logging.getLogger(__name__)
topic = Blueprint('topic', __name__)

@topic.route('/')
@login_required(next='account.login')
def index():
    page = request.args.get('p', '1')
    if not page.isdigit():
        raise abort(404)
    page = int(page)
    msg = request.args.get('msg', None)
    list_page = get_user_topics(g.current_user.id, page)
    if page >1:
        page_1 = get_user_topics(g.current_user.id, 1)
        if list_page.total != page_1 or list_page.last_time != page_1.last_time:
            backend.delete('topic:list:%d:%d' % (g.current_user.id, page))
            list_page = get_user_topics(g.current_user.id, page)
    return render_template('topic.index.html', msg=msg, \
            topics=format_topic_list(list_page.items), list_page=list_page)

@topic.route('/view/<int:tid>/')
@login_required(next='account.login')
def view(tid):
    page = request.args.get('p', '1')
    topic = get_topic(tid)
    if not topic or not page.isdigit():
        raise abort(404)
    page = int(page)
    if mark_read(g.current_user.id, tid):
        backend.delete('topic:user_topic:%d:%d' % (g.current_user.id, tid))
        backend.delete('topic:notify:%d' % g.current_user.id)
        backend.delete('topic:list:%d:1' % g.current_user.id)
    list_page = get_user_replies(tid, page)
    if page > 1 and list_page.total != get_user_replies(tid, 1):
        backend.delete('topic:replies:%d:%d' % (tid, page))
        list_page = get_user_replies(tid, page)
    #TODO check reply count!!!
    return render_template('topic.view.html', \
            replies=format_reply_list(list_page.items), \
            topic=topic, list_page=list_page)

@csrf_exempt
@topic.route('/create/<int:uid>/', methods=['GET', 'POST'])
@check_ua
@login_required(next='account.login')
def create_topic(uid):
    if uid == g.current_user.id:
        return redirect(url_for('topic.index'))
    who = get_user(uid)
    if request.method == 'GET':
        if not who:
            raise abort(404)
        return render_template('topic.create.html', uid=uid, who=who)

    to_uid = request.form.get('to_uid')
    title = request.form.get('title')
    content = request.form.get('content')

    if not who:
        #TODO return error code
        # check other params
        return render_template('topic.create.html', uid=uid)
    topic = make_topic(g.current_user.id, to_uid, title, content)
    #clean cache
    clean_cache(g.current_user.id, uid, topic.id)
    return redirect(url_for('topic.index'))

@csrf_exempt
@topic.route('/reply/<int:tid>/', methods=['GET', 'POST'])
@check_ua
@login_required(next='account.login')
def create_reply(tid):
    if request.method == 'GET':
        return redirect(url_for('topic.view', tid=tid))

    tid = request.form.get('tid')
    content = request.form.get('content')
    topic = get_topic(tid)
    sender, receiver = get_user_topics(g.current_user.id, topic.id)
    if not topic or not sender or not receiver:
        return redirect(url_for('topic.index'))
    make_reply(sender, receiver, topic, content)
    #clean cache
    clean_cache(g.current_user.id, receiver.uid, topic.id)
    backend.delete('topic:user_topic:%d:%d' % (g.current_user.id, topic.id))
    backend.delete('topic:user_topic:%d:%d' % (receiver.uid, topic.id))
    return redirect(url_for('topic.view', tid=tid))

@topic.route('/delete/<int:tid>/')
@check_ua
@login_required(next='account.login')
def topic_delete(tid):
    user_topic = get_user_topic(g.current_user.id, tid=tid)
    if user_topic:
        delete_topic(user_topic)
        backend.delete('topic:meta:%d' % g.current_user.id)
        backend.delete('topic:list:%d:1' % g.current_user.id)
        backend.delete('topic:user_topic:%d:%d' % (g.current_user.id, tid))
    return redirect(url_for('topic.index'))

def clean_cache(uid, to_uid, tid):
    backend.delete('topic:topic:%d' % tid)
    backend.delete('topic:replies:%d:1' % tid)
    backend.delete('topic:list:%d:1' % uid)
    backend.delete('topic:list:%d:1' % to_uid)
    backend.delete('topic:notify:%d' % to_uid)
    backend.delete('topic:meta:%d' % uid)
    backend.delete('topic:meta:%d' % to_uid)
    cross_cache.delete('open:account:unread:{0}'.format(to_uid))

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

