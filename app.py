#!/usr/bin/python
# encoding: UTF-8

import os
import config
import logging

from models import *
from views.oauth import oauth
from views.account import account
from sheep.api.permdir import permdir
from sheep.api.statics import static_files
from beaker.middleware import SessionMiddleware

from flaskext.csrf import csrf
from flask import Flask, render_template, \
        request, url_for, g

app = Flask(__name__)
app.debug = config.DEBUG
app.jinja_env.filters['s_files'] = static_files

app.config.update(
    SQLALCHEMY_DATABASE_URI = config.DATABASE_URI,
    SQLALCHEMY_POOL_SIZE = 1000,
    SQLALCHEMY_POOL_RECYCLE = True
)

session_opts = {
    'session.type': 'ext:database',
    'session.url': config.DATABASE_URI,
    'session.table_name': 'sessions',
    'session.lock_dir': os.path.join(permdir, 'lockdir'),
    'session.auto' : False,
    'session.cookie_expires': True,
    'session.cookie_path': '/',
    'session.cookie_domain': config.SESSION_COOKIE_DOMAIN,
    'session.timeout': 86400
}

oauth.register_blueprints(app)
app.register_blueprint(account, url_prefix='/account')
logger = logging.getLogger(__name__)

init_db(app)
csrf(app)
app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts, key=config.SESSION_KEY)

@app.route('/')
def index():
    if g.user is None:
        return render_template('index.html', login_url=url_for('account.login'))
    return render_template('index.html', login=1)

@app.before_request
def before_request():
    g.user = None
    session = request.environ['beaker.session']
    g.session = session
    if 'user_id' in session and session['user_id']:
        if not session.get('user', None):
            session['user'] = User.query.get(session['user_id'])
        g.user = session['user']
        g.oauth = lambda otype: OAuth.query.filter_by(oauth_type=otype, uid=g.user.id).first()

@app.after_request
def after_request(resp):
    g.session.save()
    return resp

@app.errorhandler(404)
def page_not_found(e):
    return render_template('40x.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('40x.html'), 500

@app.route('/test1')
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
