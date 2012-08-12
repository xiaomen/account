#!/usr/local/bin/python2.7
#coding:utf-8

class Obj(object):pass

def gen_list_page_obj(page_obj):
    if not page_obj:
        return None
    list_page = Obj()
    list_page.items = page_obj.items
    list_page.has_next = page_obj.has_next
    list_page.has_prev = page_obj.has_prev
    list_page.next_num = page_obj.next_num
    list_page.page = page_obj.page
    list_page.pages = page_obj.pages
    list_page.total = page_obj.total
    list_page.iter_pages = xrange(1, page_obj.pages+1)
    return list_page
