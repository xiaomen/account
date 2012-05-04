#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 crackcell
#

import re
import logging
from urlparse import urlparse

from utils import *
from models.mail import *
from sheep.api.cache import backend
from flask import render_template, redirect, \
    request, url_for, g, Blueprint, abort

logger = logging.getLogger(__name__)

mail = Blueprint('mail', __name__)

class mail_obj: pass

def gen_maillist(mails, key, pos=0):
    mail_list = []
    for mail in mails:
        from_user = get_user(getattr(mail, key))
        if not from_user or not int(mail.is_show[pos]):
            continue
        m = mail_obj()
        setattr(m, key, from_user.name)
        setattr(m, key+'_url', from_user.domain or from_user.id)
        m.id = mail.id
        m.title = mail.title
        m.is_read = mail.is_read
        mail_list.append(m)
    return mail_list

@mail.route('/')
def index():
    return inbox()

@mail.route('/inbox')
def inbox():
    user = get_current_user()
    if not user:
        return redirect(url_for('account.login'))

    mails = get_mail_inbox_all(user.id)
    mails = gen_maillist(mails, 'from_uid')

    return render_template('inbox.html', mails = mails)

@mail.route('/outbox')
def outbox():
    user = get_current_user()
    if not user:
        return redirect(url_for('account.login'))

    mails = get_mail_outbox_all(user.id)
    mails = gen_maillist(mails, 'to_uid', -1)

    return render_template('outbox.html', mails = mails)

@mail.route('/view/<mail_id>')
def view(mail_id):
    box = request.headers.get('Referer', '')
    box = urlparse(box)

    if url_for('mail.index') == box.path or \
            url_for('mail.inbox') == box.path:
        box = 'inbox'
    elif url_for('mail.outbox') == box.path:
        box = 'outbox'
    else:
        box = None

    if not box:
        return redirect(url_for('mail.index'))

    user = get_current_user()
    if not user:
        return redirect(url_for('account.login'))

    mail = get_mail(mail_id)
    #TODO ugly
    if not mail:
        raise abort(404)

    if not check_mail_access(user.id, mail):
        return redirect(url_for('mail.index'))

    Mail.mark_as_read(mail)

    mobj = mail_obj()
    mobj.id = mail_id
    mobj.delete = '%s/%s' %(box, str(mail_id))
    from_user = get_user(mail.from_uid)
    mobj.from_uid = from_user.name
    mobj.from_uid_url = from_user.domain or from_user.id
    mobj.title = mail.title
    mobj.content = mail.content

    backend.delete('mail:unread:%d' % user.id)
    backend.delete('mail:inbox:%d' % user.id)

    if box == 'inbox':
        return render_template('view.html', mail = mobj, reply=1)
    else:
        return render_template('view.html', mail = mobj)

@mail.route('/delete/<box>/<mail_id>')
def delete(box, mail_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('account.login'))

    mail = get_mail(mail_id)
    if not mail or box not in ['inbox', 'outbox'] or \
            not check_mail_access(user.id, mail):
        return redirect(url_for('mail.index'))

    if box == 'inbox':
        Mail.delete_inbox(mail)
        backend.delete('mail:inbox:%d' % user.id)
    elif box == 'outbox':
        Mail.delete_outbox(mail)
        backend.delete('mail:outbox:%d' % user.id)

    return redirect(url_for('mail.index'))

@mail.route('/write', methods=['GET', 'POST'])
def write():
    user = get_current_user()
    if not user:
        return redirect(url_for('account.login'))

    if request.method == 'GET':
        to_uid = request.args.get('to')
        reply_mid = request.args.get('reply')
        title = ''
        content = ''
        if reply_mid:
            mail = get_mail(reply_mid)
            if user.id != mail.to_uid:
                return redirect(url_for('mail.index'))
            to_uid = mail.from_uid
            title = reply_mail_title(mail.title)
            content = '--------\n%s\n--------\n' % mail.content
        who = get_user(to_uid)
        if not to_uid or not who:
            return redirect(url_for('mail.index'))
        return render_template('write.html', who=who, \
                title=title, content=content)

    to_uid = request.form.get('to_uid')
    title = request.form.get('title')
    content = request.form.get('content')

    who = get_user(to_uid)
    error = check_mail(who, title, content)
    if error is not None:
        return render_template('write.html', who=who, \
                title=title, content=content, error=error)

    Mail.create(from_uid = user.id,
                to_uid = who.id,
                title = title,
                content = content)

    #clean cache
    backend.delete('mail:inbox:%s' % who.id)
    backend.delete('mail:unread:%s' % who.id)
    backend.delete('mail:outbox:%d' % user.id)

    return redirect(url_for('mail.index'))

def reply_mail_title(title):
    if not isinstance(title, unicode):
        title = unicode(title, 'utf-8')
    m = re.search(ur'^Re\((?P<num>\d+)\):[\u4e00-\u9fa5\w]+$', title)
    if not m:
        return 'Re(1):' + title
    num = int(m.group('num')) + 1
    title = title.replace('Re(%s)' % m.group('num'), 'Re(%d)' % num, 1)
    return title


