#!/usr/local/bin/python2.7
#coding:utf-8

import logging
from flask import g, request, Blueprint

logger = logging.getLogger(__name__)

people = Blueprint('people', __name__)

