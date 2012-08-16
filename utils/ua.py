# -*- coding: utf-8 -*- 
# AUTHOR: Zeray Rice <fanzeyi1994@gmail.com>
# FILE: utils/ua.py
# CREATED: 04:14:53 10/08/2012
# MODIFIED: 22:29:58 16/08/2012

import flask
from flask import request
from functools import wraps
from werkzeug.useragents import UserAgent

def check_ua(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        ua = UserAgent(request.headers.get('User-Agent'))
        if ua.browser == 'msie':
            try:
                if int(float(ua.version)) < 8:
                    return render_template("noie.html")
            except:
                return render_template("noie.html")
        return method(*args, **kwargs) 
    return wrapper

def render_template(template_name, *args, **kwargs):
    ua_string = request.headers.get('User-Agent')
    if not ua_string:
        return flask.render_template("mobile/" + template_name, *args, **kwargs) 
    ua = UserAgent(ua_string)
    if ua.platform and ua.platform.lower() in ["android", "iphone"]:
        return flask.render_template("mobile/" + template_name, *args, **kwargs)
    return flask.render_template(template_name, *args, **kwargs)
