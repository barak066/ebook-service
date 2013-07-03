#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from . import Info

class BookInfo(Info):
    "stores info about book, presents convenient access to book info"
    def __init__(self):
        self.title = None
        self.authors = []
        self.pagelink = None
        self.language = '?'
        self.summary = None
        self.links = {}
        self.tags = []
        self.image = None

    def _get_full(self):
        return [('Title' , self.title),
                ('Authors' , self.authors),
                ('Image' , self.image),
                ('Links' , self.links),
                ('Language' , self.language),
                ('Pagelink' , self.pagelink),
                ('Tags' , self.tags),
                ('Summary' , self.summary),
               ]


    def _get_short(self):
        return [ ('Title' , self.title),
                 ('Link' , self.pagelink),
               ]



  