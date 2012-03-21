#!/usr/local/bin/python2.7
#coding:utf-8

import re
import email
import config
import smtplib
from flask import g
from models import db, User, Forget

def get_current_user():
    if not g.session or not g.session.get('user_id') or not g.session.get('user_token'):
        return None
    user = get_user(g.session['user_id'])
    if not user or g.session['user_token'] != user.token:
        return None
    return user

def send_email(to_add, subject, html, from_add=config.SMTP_USER):
    if isinstance(to_add, list):
        to_add = ','.join(to_add)

    msg_root = email.MIMEMultipart.MIMEMultipart('related')
    msg_root['Subject'] = subject
    msg_root['From'] = from_add
    msg_root['To'] = to_add
    msg_root.preamble = 'Xiaomen.co account service'

    msg_alternative = email.MIMEMultipart.MIMEMultipart('alternative')
    msg_root.attach(msg_alternative)
    msg_html = email.MIMEText.MIMEText(html, 'html', 'utf-8')
    msg_alternative.attach(msg_html)

    smtp = smtplib.SMTP()
    smtp.set_debuglevel(1)
    smtp.connect(config.SMTP_SERVER)
    smtp.login(config.SMTP_USER, config.SMTP_PASSWORD)
    smtp.sendmail(from_add, to_add, msg_root.as_string())
    smtp.quit()

#cache
def get_user(username):
    try:
        username = int(username)
        return User.query.get(username)
    except:
        if check_domain(username):
            return None
        return get_user_by(domain=username).first()

#cache
def get_user_by(**kw):
    return User.query.filter_by(**kw)

#cache
def get_forget_by(**kw):
    return Forget.query.filter_by(**kw)

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
    user = get_user_by(domain=domain).first()
    if user:
        return False, 'domain exists'

if __name__ == '__main__':
    send_email('ilskdw@126.com', 'xiaomenco account service', '<p>hello world</p>')
