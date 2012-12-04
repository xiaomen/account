#!/usr/local/bin/python2.7
#coding:utf-8

import logging
from PIL import Image
from functools import wraps
from cStringIO import StringIO
from config import ALLOWED_EXTENSIONS
from flask import g, url_for, redirect, request

logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def process_file(user, upload_file):
    if not allowed_file(upload_file.filename):
        return None, None, 'invalid %s' % upload_file.filename
    suffix = upload_file.filename.rsplit('.', 1)[1]
    filename = 'u%d.jpg' % user.id
    stream = upload_file.stream
    error = None
    if suffix == 'png' or suffix == 'gif':
        try:
            stream = StringIO()
            image = Image.open(upload_file.stream)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(stream, 'jpeg')
            stream.getvalue()
            stream.seek(0)
        except Exception, e:
            logger.exception('convert error')
            error = str(e)
    return filename, stream, error

def login_required(next=None, need=True, *args, **kwargs):
    def _login_required(f):
        @wraps(f)
        def _(*args, **kwargs):
            import pdb
            pdb.set_trace()
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

