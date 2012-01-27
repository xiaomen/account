#!/usr/bin/python
# encoding: UTF-8

import config
import logging

from models import *
from views.oauth import oauth
from views.account import account
from sheep.api.statics import static_files

from flaskext.csrf import csrf
from flask import Flask, render_template, session, g

app = Flask(__name__)
app.debug = config.DEBUG
app.secret_key = config.SECRET_KEY
app.jinja_env.filters['s_files'] = static_files

app.config.update(
    SQLALCHEMY_DATABASE_URI = config.DATABASE_URI,
    SQLALCHEMY_POOL_SIZE = 1000,
    SQLALCHEMY_POOL_RECYCLE = True
)

oauth.register_blueprints(app)
app.register_blueprint(account, url_prefix='/account')
logger = logging.getLogger(__name__)

init_db(app)
csrf(app)

@app.route('/')
def index():
    if g.user is None:
        return render_template('index.html')
    else:
        return render_template('index.html', login=1)

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session and session['user_id']:
        if not session.get('user', None):
            session['user'] = User.query.get(session['user_id'])
        g.user = session['user']
        g.oauth = lambda otype: OAuth.query.filter_by(oauth_type=otype, uid=g.user.id).first()

@app.route('/test')
def test():
    if g.user is None:
        return render_template('index.html')
    else:
        from lib.weibo import weibo
        from lib.douban import douban
        from lib.qq import qq
        from lib.renren import renren
        #oauth_info = g.oauth('weibo')
        #output_userinfo(weibo, oauth_info, '/users/show.json', \
        #    {'uid' :oauth_info.oauth_uid}, {'Authorization' : 'OAuth2 %s' % weibo.tokengetter_func()})

        oauth_info = g.oauth('douban')
        output_userinfo(douban, oauth_info, '/people/@me?alt=json',
            headers = {'Authorization' : 'Bearer %s' % douban.tokengetter_func()})

        #oauth_info = g.oauth('renren')
        #output_userinfo(renren, oauth_info, 'users.getInfo', {'access_token': renren.tokengetter_func()})

        return 'Hello World'

def output_userinfo(o, oauth_info, url, data=None, headers=None):
    if not oauth_info:
        return None
    user_info = o.request(url, data, headers)
    print user_info.data
