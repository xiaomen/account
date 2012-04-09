#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 crackcell
#

import logging

from utils import *
from models.mail import *
from sheep.api.cache import backend
from flask import Flask, render_template, redirect, \
    request, url_for, g, Blueprint

logger = logging.getLogger(__name__)

mail = Blueprint('mail', __name__)

@mail.route('/')
def index():
    return recv()

@mail.route('/recv')
def recv():
    if not get_current_user():
        return redirect(url_for('account.login'))

    uid = g.session['user_id']

    mails = get_mail_recv_all(uid)
    return render_template('recv.html', mails = mails)

@mail.route('/sent')
def sent():
    if not get_current_user():
        return redirect(url_for('account.login'))

    uid = g.session['user_id']

    mails = get_mail_sent_all(uid)
    return render_template('sent.html', mails = mails)

@mail.route('/view/<mail_id>')
def view(mail_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('account.login'))

    #TODO SQL inject
    mail = get_mail(mail_id)
    Mail.mark_as_read(mail)
    backend.delete('mail:unread:%d' % user.id)
    backend.delete('mail:recv:%d' % user.id)

    return render_template('view.html', mail = mail)

@mail.route('/write', methods=['GET', 'POST'])
def write():
    user = get_current_user()
    if not user:
        return redirect(url_for('account.login'))

    #TODO SQL inject and cache
    to_uid = request.form.get('to_uid')
    if (request.method == 'GET'):
        return render_template('write.html')

    Mail.create(from_uid = user.id,
                to_uid = to_uid,
                title = request.form.get('title'),
                content = request.form.get('content'))

    #clean cache
    backend.delete('mail:recv:%s' % to_uid)
    backend.delete('mail:unread:%s' % to_uid)
    backend.delete('mail:sent:%d' % user.id)

    return redirect(url_for('mail.index'))

