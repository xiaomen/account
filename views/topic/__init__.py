#!/usr/local/bin/python2.7
#coding:utf-8

from flask import Blueprint

from views.topic.view import View
from views.topic.index import Index
from views.topic.delete import Delete
from views.topic.reply import CreateReply
from views.topic.topic import CreateTopic

topic = Blueprint('topic', __name__)

view = View.as_view('view')
index = Index.as_view('index')
delete = Delete.as_view('topic_delete')
create_reply = CreateReply.as_view('create_reply')
create_topic = CreateTopic.as_view('create_topic')

topic.add_url_rule('/', view_func=index, methods=['GET'])
topic.add_url_rule('/view/<int:tid>/', view_func=view, methods=['GET'])
topic.add_url_rule('/delete/<int:tid>/', view_func=delete, methods=['GET'])
topic.add_url_rule('/reply/<int:tid>/', view_func=create_reply, methods=['GET', 'POST'])
topic.add_url_rule('/create/<int:uid>/', view_func=create_topic, methods=['GET', 'POST'])

