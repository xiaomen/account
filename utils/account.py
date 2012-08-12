#!/usr/local/bin/python2.7
#coding:utf-8

from functools import wraps
from flask import url_for, redirect

def login_required(next=None, need=True, *args, **kwargs):
    def _login_required(f):
        @wraps(f)
        def _(*args, **kwargs):
            if (need and not g.current_user) or \
                    (not need and g.current_user):
                if next:
                    return redirect(url_for(next, *args, **kwargs))
                return url_for('index')
            return f(*args, **kwargs)
        return _
    return _login_required

