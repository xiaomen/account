#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import datetime, time
from sheep.api.mysql import connect, get_mysql_conn_params

logger = logging.getLogger()

def main():
    while 1:
        d = connect()
        c = d.cursor()
        c.execute('SELECT * FROM users;')
        print c.fetchall()
        print get_mysql_conn_params()
        logger.info(datetime.datetime.now())
        time.sleep(5)

if __name__ == '__main__':
    main()
