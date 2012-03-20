#!/usr/local/bin/python2.7
#coding:utf-8

import json
import logging
from .account import _logout, check_login_info
from models import db, User
from flask import g, request, jsonify, Blueprint
from flaskext.csrf import csrf_exempt

logger = logging.getLogger(__name__)

api = Blueprint('api', __name__)

@csrf_exempt
@api.route('/login', methods=['POST'])
def api_login():
    if g.user:
        user = User.query.get(g.user)
        return jsonify(status='logged in', id=user.id, \
                email=user.email, name=user.name)
    data = json.loads(request.data)
    password = data.get('password')
    email = data.get('email', None)
    check, error = check_login_info(email, password)
    if not check:
        return jsonify(status='error', error=error)

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(status='error', error='no such user')
    if not user.check_password(password):
        return jsonify(status='error', error='invaild passwd')

    g.session['user_id'] = user.id
    return jsonify(status='ok', user_id=user.id, \
            email=user.email, name=user.name)

@api.route('/logout')
def api_logout():
    _logout()
    return jsonify(status='ok')
