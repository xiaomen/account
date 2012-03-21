#!/usr/local/bin/python2.7
#coding:utf-8

import re
from flask import g
from models import db, User, Profile

def get_current_user():
    if not g.session or not g.session.get('user_id') or not g.session.get('user_token'):
        return None
    user = get_user(g.session['user_id'])
    if not user or g.session['user_token'] != user.token:
        return None
    return user

#cache
def get_user(username):
    try:
        username = int(username)
        return User.query.get(username)
    except:
        if check_domain(username):
            return None
        profile = get_profile_by(domain=username).first()
        if not profile:
            return None
        return User.query.get(profile.uid)

#cache
def get_user_by(**kw):
    return User.query.filter_by(**kw)

#cache
def get_profile_by(**kw):
    return Profile.query.filter_by(**kw)

def check_password(password):
    if not password:
        return False, 'need password'
    if not re.search(r'[\S]{6,}', password, re.I):
        return False, 'password invaild'

def check_domain(domain):
    if not domain:
        return False, 'need domain'
    if not re.search(r'^[a-zA-Z0-9_-]{4,10}$', domain, re.I):
        return False, 'domain invail'

def check_username(username):
    if not username:
        return False, 'need username'
    if not re.search(r'^[a-zA-Z0-9_-]{3,20}$', username, re.I):
        return False, 'username invail'

def check_email(email):
    if not email:
        return False, 'need email'
    if not re.search(r'^.+@[^.].*\.[a-z]{2,10}$', email, re.I):
        return False, 'email invaild'

def check_email_exists(email):
    if not email:
        return False, 'need email'
    user = get_user_by(email=email).first()
    if user:
        return False, 'email exists'

def check_domain_exists(domain):
    if not domain:
        return False, 'need domain'
    profile = get_profile_by(domain=domain).first()
    if profile:
        return False, 'domain exists'
