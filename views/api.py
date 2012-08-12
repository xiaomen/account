#!/usr/local/bin/python2.7
#coding:utf-8

import logging
from models.account import db, User
from utils import get_user_by_email, get_user,\
        get_unread_mail_count
from flaskext.csrf import csrf_exempt
from flask import g, request, jsonify, Blueprint
from .account import account_logout, account_login, \
        check_login_info, check_register_info, \
        clear_user_cache

logger = logging.getLogger(__name__)

api = Blueprint('api', __name__)

@csrf_exempt
@api.route('/register', methods=['POST'])
def register():
    data = request.json
    password = data.get('password', None)
    email = data.get('email', None)
    username = data.get('name', None)
    check, error = check_register_info(username, email, password)
    if not check:
        return jsonify(status='error', error=error)
    user = User(username, password, email)
    db.session.add(user)
    db.session.commit()
    #clear cache
    clear_user_cache(user)
    account_login(user)
    return jsonify(status='register ok and logged in', id=user.id, \
            email=user.email, name=user.name)

@csrf_exempt
@api.route('/login', methods=['POST'])
def api_login():
    data = request.json
    password = data.get('password', None)
    email = data.get('email', None)
    check, error = check_login_info(email, password)
    if not check:
        return jsonify(status='error', error=error)

    user = get_user_by_email(email=email)
    if not user:
        return jsonify(status='error', error='no such user')
    if not user.check_password(password):
        return jsonify(status='error', error='invaild passwd')

    account_login(user)
    return jsonify(status='ok', user_id=user.id, \
            email=user.email, name=user.name)

@api.route('/logout')
def api_logout():
    account_logout()
    return jsonify(status='ok')

@api.route('/unread/<int:id>')
def api_unread(id):
    num = get_unread_mail_count(int(id))
    return jsonify(count=num)

@api.route('/people/<username>')
def api_people(username):
    people = get_user(username)
    if people:
        return jsonify(status='ok', name=people.name, uid=people.id)
    return jsonify(status='not found')

