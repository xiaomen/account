#!/usr/local/bin/python2.7
#coding:utf-8

import logging

from flask import Blueprint

logger = logging.getLogger(__name__)

topic = Blueprint('topic', __name__)
