#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 crackcell
#

import logging
from utils import *
from models.mail import *
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

    mails = Mail.get_recv_all(uid)
    return render_template('recv.html', mails = mails,
                           unread_mail_count =
                           Notification.get_unread_mail_count(uid))

@mail.route('/sent')
def sent():
    if not get_current_user():
        return redirect(url_for('account.login'))

    uid = g.session['user_id']

    mails = Mail.get_sent_all(uid)
    return render_template('sent.html', mails = mails,
                           unread_mail_count =
                           Notification.get_unread_mail_count(uid))

@mail.route('/view')
def view():
    if not get_current_user():
        return redirect(url_for('account.login'))

    uid = g.session['user_id']

    mid = request.args.get('id', '')

    #TODO SQL inject and cache
    mail = Mail.query.filter_by(id = mid).first()
    return render_template('view.html', mail = mail,
                           unread_mail_count =
                           Notification.get_unread_mail_count(uid))

@mail.route('/write', methods=['GET', 'POST'])
def write():
    if not get_current_user():
        return redirect(url_for('account.login'))

    uid = g.session['user_id']
    #TODO SQL inject and cache
    to_uid = request.form.get('to_uid')
    if (request.method == 'GET'):
        return render_template('write.html',
                               unread_mail_count =
                               Notification.get_unread_mail_count(uid))

    Mail.insert(from_uid = uid,
                to_uid = to_uid,
                title = request.form.get('title'),
                content = request.form.get('content'))
    Notification.increase_unread(to_uid)
    return redirect(url_for('mail.index'))

