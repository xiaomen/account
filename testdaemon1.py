#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import datetime, time

logger = logging.getLogger(__name__)

def main():
    while 1:
        logging.info(datetime.datetime.now())
        time.sleep(5)

if __name__ == '__main__':
    main()
