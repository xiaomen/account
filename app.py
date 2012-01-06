#!/usr/bin/python
# encoding: UTF-8

from sheep.api.statics import static_files
from flask import Flask, request, redirect, session, render_template
from lib.weibo import OAuthHandler, oauth, API

app = Flask(__name__)
app.debug = True
app.secret_key = 'sheep!user#$@!v1'
app.jinja_env.filters['s_files'] = static_files

consumer_key = '619662253'
consumer_secret = 'b1d02f2ff16aec904d835d34bc926ae7'

@app.route('/')
def hello():
    return render_template('index.html')

