#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 crackcell
#

import logging

from utils import *
from models.mail import *
from sheep.api.cache import backend
from flask import render_template, redirect, \
    request, url_for, g, Blueprint, abort

logger = logging.getLogger(__name__)

mail = Blueprint('mail', __name__)

class mail_obj: pass

def gen_maillist(mails, key):
    maillist = []
    for mail in mails:
        from_user = get_user(getattr(mail, key))
        if not from_user:
            continue
        m = mail_obj()
        setattr(m, key, from_user.name)
        setattr(m, key+'_url', from_user.domain or from_user.id)
        m.id = mail.id
        m.title = mail.title
        m.is_read = mail.is_read
        maillist.append(m)
    return maillist

@mail.route('/')
def index():
    return recv()

@mail.route('/recv')
def recv():
    user = get_current_user()
    if not user:
        return redirect(url_for('account.login'))

    mails = get_mail_recv_all(user.id)
    mails = gen_maillist(mails, 'from_uid')

    return render_template('recv.html', mails = mails)

@mail.route('/sent')
def sent():
    user = get_current_user()
    if not user:
        return redirect(url_for('account.login'))

    mails = get_mail_sent_all(user.id)
    mails = gen_maillist(mails, 'to_uid')

    return render_template('sent.html', mails = mails)

@mail.route('/view/<mail_id>')
def view(mail_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('account.login'))

    mail = get_mail(mail_id)
    if not mail:
        raise abort(404)

    if not check_mail_access(user.id, mail):
        return recv()
    Mail.mark_as_read(mail)

    mobj = mail_obj()
    from_user = get_user(mail.from_uid)
    mobj.from_uid = from_user.name
    mobj.from_uid_url = from_user.domain or from_user.id
    mobj.title = mail.title
    mobj.content = mail.content

    backend.delete('mail:unread:%d' % user.id)
    backend.delete('mail:recv:%d' % user.id)

    return render_template('view.html', mail = mobj)

@mail.route('/write', methods=['GET', 'POST'])
def write():
    user = get_current_user()
    if not user:
        return redirect(url_for('account.login'))

    if request.method == 'GET':
        to_uid = request.args.get('to')
        who = get_user(to_uid)
        if not to_uid or not who:
            return recv()
        return render_template('write.html', to_uid=to_uid, who=who)

    to_uid = request.form.get('to_uid')
    title = request.form.get('title')
    content = request.form.get('content')

    error = check_mail(to_uid, title, content)
    if error is not None:
        who = get_user(to_uid)
        return render_template('write.html', to_uid=to_uid, \
                who=who, title=title, content=content, error=error)

    Mail.create(from_uid = user.id,
                to_uid = to_uid,
                title = title,
                content = content)

    #clean cache
    backend.delete('mail:recv:%s' % to_uid)
    backend.delete('mail:unread:%s' % to_uid)
    backend.delete('mail:sent:%d' % user.id)

    return recv()

