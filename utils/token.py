#!/usr/local/bin/python2.7
#coding:utf-8

import string
import random
import logging
from utils.redistore import redistore
from config import TOKEN_LENGTH, TOKEN_EXPIRE, \
        TOKEN_UID, TOKEN_TOKEN

letters = string.letters + string.digits

logger = logging.getLogger(__name__)

def make_token(uid, expire=TOKEN_EXPIRE):
    #check if user got a token
    uid_key = TOKEN_UID % uid
    key = redistore.get(uid_key)
    if key:
        return key

    token = ''.join(random.sample(letters, TOKEN_LENGTH))
    key = TOKEN_TOKEN % token
    while redistore.get(key):
        token = ''.join(random.sample(letters, TOKEN_LENGTH))
        key = TOKEN_TOKEN % token
    pipe = redistore.pipeline()
    pipe.setex(key, uid, expire)
    pipe.setex(uid_key, token, expire)
    logger.info(pipe.execute())
    return token

def validate_token(uid, token):
    key = TOKEN_TOKEN % token
    value = redistore.get(key)
    if not value:
        return False
    if int(value) != uid:
        return False
    pipe = redistore.pipeline()
    pipe.delete(key)
    pipe.delete(TOKEN_UID % uid)
    logger.info(pipe.execute())
    return True

def get_uid(token):
    key = TOKEN_TOKEN % token
    value = redistore.get(key)
    if not value:
        return -1
    value = int(value)
    pipe = redistore.pipeline()
    pipe.delete(key)
    pipe.delete(TOKEN_UID % value)
    logger.info(pipe.execute())
    return value

if __name__ == '__main__':
    token1 = make_token(1, 60)
    print token1
    print make_token(1, 3) == token1
    print validate_token(1, token1)
    token2 = make_token(1, 3)
    print token1 != token2
    import time
    time.sleep(4)
    print validate_token(1, token1)

