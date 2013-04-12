#!/usr/local/bin/python2.7
#coding:utf-8

from flask import Blueprint

from views.people.people import People

people = Blueprint('people', __name__)

people_view = People.as_view('show_people')
people.add_url_rule('/<username>/', view_func=people_view, methods=['GET'])

