#!/usr/local/bin/python2.7
#coding:utf-8

from functools import wraps
from config import ALLOWED_EXTENSIONS
from flask import g, url_for, redirect, request

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def login_required(next=None, need=True, *args, **kwargs):
    def _login_required(f):
        @wraps(f)
        def _(*args, **kwargs):
            if (need and not g.current_user) or \
                    (not need and g.current_user):
                if next:
                    if next != 'account.login':
                        url = url_for(next)
                    else:
                        url = url_for(next, redirect=request.url)
                    return redirect(url)
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return _
    return _login_required

