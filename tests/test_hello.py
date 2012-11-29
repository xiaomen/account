#!/usr/local/bin/python2.7
#coding:utf-8

from sheep.api.test import TestCase

class TestHello(TestCase):
    def setUp(self):
        super(TestHello, self).setUp()

    def test_hello(self):
        hello = 1
        self.assertEqual(hello, 1)

