#!/usr/local/bin/python2.7
#coding:utf-8

from models.account import OAuth

def create_oauth(uid, ouid, otype):
    return OAuth.create(uid, ouid, otype)

