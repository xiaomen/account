#!/usr/local/bin/python2.7
#coding:utf-8

from lxml import etree
from pyquery import PyQuery as pq

class Message(object):
    def __init__(self, data):
        self.t = pq(etree.fromstring(data), parser = "xml")
        self.To = self.t("ToUserName").text()
        self.From = self.t("FromUserName").text()
        self.Type = self.t("MsgType").text()
        self.Body = self.t("Content").text().strip()

