#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 crackcell
#

import re
import logging
from urlparse import urlparse, parse_qs

from utils.validators import check_mail_access, \
        check_mail
from utils.ua import render_template
from utils.helper import Obj
from utils.account import login_required
from query.mail import get_inbox_mail, get_inbox_count, \
        get_outbox_mail, get_outbox_count, get_mail, \
        create_mail
from query.account import get_user
from sheep.api.cache import backend, cross_cache
from flask import redirect, \
    request, url_for, g, Blueprint, abort

logger = logging.getLogger(__name__)

mail = Blueprint('mail', __name__)

def gen_maillist(mails, key):
    if not mails:
        return
    for mail in mails.items:
        from_user = get_user(getattr(mail, key))
        if not from_user:
            continue
        m = Obj()
        m.id = mail.id
        m.user = from_user
        m.title = mail.title
        m.is_read = mail.is_read
        yield m

@mail.route('/')
@login_required(next='account.login')
def index():
    return inbox()

@mail.route('/inbox/')
@mail.route('/inbox/<int:page>')
@login_required(next='account.login')
def inbox(page=1):
    list_page = get_inbox_mail(g.current_user.id, page)

    #check modify
    total_mail_num = get_inbox_count(g.current_user.id)
    if total_mail_num != list_page.total:
        backend.delete('mail:inbox:%d:%d' % (g.current_user.id, int(page)))
        list_page = get_inbox_mail(g.current_user.id, page)

    mails = gen_maillist(list_page, 'from_uid')

    return render_template('mail.inbox.html', mails = mails, \
            list_page = list_page)

@mail.route('/outbox/')
@mail.route('/outbox/<int:page>')
@login_required(next='account.login')
def outbox(page=1):
    list_page = get_outbox_mail(g.current_user.id, page)

    #check modify
    total_mail_num = get_outbox_count(g.current_user.id)
    if total_mail_num != list_page.total:
        backend.delete('mail:outbox:%d:%d' % (g.current_user.id, int(page)))
        list_page = get_outbox_mail(g.current_user.id, page)

    mails = gen_maillist(list_page, 'to_uid')

    return render_template('mail.outbox.html', mails = mails, \
            list_page = list_page)

@mail.route('/view/<int:mid>/')
@login_required(next='account.login')
def view(mid):
    box = request.headers.get('Referer', '')
    box = urlparse(box)
    query = parse_qs(box.query)

    if url_for('mail.index') == box.path or \
            url_for('mail.inbox') == box.path:
        box = 'inbox'
    elif url_for('mail.outbox') == box.path:
        box = 'outbox'
    else:
        box = None

    if not box:
        return redirect(url_for('mail.index'))

    mail = get_mail(mid)
    #TODO ugly
    if not mail:
        raise abort(404)

    if not check_mail_access(g.current_user.id, mail):
        return redirect(url_for('mail.index'))

    if not mail.is_read and mail.to_uid == g.current_user.id:
        page = query.get('p', [])
        if not page:
            page = 1
        else:
            page = int(page[0])
        mail.mark_as_read()
        backend.delete('mail:inbox:%d:%d' % (g.current_user.id, page))
        clean_unread_cache(g.current_user.id)

    mobj = Obj()
    mobj.id = mid
    mobj.box = box
    from_user = get_user(mail.from_uid)
    mobj.from_uid = from_user.name
    mobj.from_uid_url = from_user.domain or from_user.id
    mobj.title = mail.title
    mobj.content = mail.content

    if box == 'inbox':
        return render_template('mail.view.html', mail = mobj, reply=1)
    else:
        return render_template('mail.view.html', mail = mobj)

@mail.route('/delete/<box>/<int:mid>/')
@login_required(next='account.login')
def delete(box, mid):
    mail = get_mail(mid)
    if not mail or box not in ['inbox', 'outbox'] or \
            not check_mail_access(g.current_user.id, mail):
        return redirect(url_for('mail.index'))

    if box == 'inbox':
        mail.delete_inbox()
        backend.delete('mail:inbox:%d:1' % g.current_user.id)
        backend.delete('mail:inbox:count:%d' % g.current_user.id)
    elif box == 'outbox':
        mail.delete_outbox()
        backend.delete('mail:outbox:%d:1' % g.current_user.id)
        backend.delete('mail:outbox:count:%d' % g.current_user.id)

    return redirect(url_for('mail.index'))

@mail.route('/write/', methods=['GET', 'POST'])
@login_required(next='account.login')
def write():
    if request.method == 'GET':
        to_uid = request.args.get('to')
        reply_mid = request.args.get('reply')
        title = ''
        content = ''
        if not to_uid and not reply_mid:
            return redirect(url_for('mail.index'))
        if reply_mid:
            mail = get_mail(reply_mid)
            if g.current_user.id != mail.to_uid:
                return redirect(url_for('mail.index'))
            to_uid = mail.from_uid
            title = reply_mail_title(mail.title)
            content = '--------\n%s\n--------\n' % mail.content
        who = get_user(to_uid)
        if not who:
            return redirect(url_for('mail.index'))
        return render_template('mail.write.html', who=who, \
                title=title, content=content)

    to_uid = request.form.get('to_uid')
    title = request.form.get('title')
    content = request.form.get('content')
    who = get_user(to_uid)

    error = check_mail(who, title, content)
    if error is not None:
        return render_template('mail.write.html', who=who, \
                title=title, content=content, error=error)

    create_mail(from_uid = g.current_user.id,
                to_uid = who.id,
                title = title,
                content = content)

    #clean cache
    backend.delete('mail:outbox:%d:1' % g.current_user.id)
    backend.delete('mail:outbox:count:%d' % g.current_user.id)
    backend.delete('mail:inbox:%d:1' % who.id)
    backend.delete('mail:inbox:count:%d' % who.id)
    clean_unread_cache(who.id)
    return redirect(url_for('mail.index'))

def clean_unread_cache(uid):
    backend.delete('mail:unread:{0}'.format(uid))
    cross_cache.delete('open:account:unread:{0}'.format(uid))

def reply_mail_title(title):
    if not isinstance(title, unicode):
        title = unicode(title, 'utf-8')
    m = re.search(ur'^Re\((?P<num>\d+)\):[\u4e00-\u9fa5\w]+$', title)
    if not m:
        return 'Re(1):' + title
    num = int(m.group('num')) + 1
    title = title.replace('Re(%s)' % m.group('num'), 'Re(%d)' % num, 1)
    return title

