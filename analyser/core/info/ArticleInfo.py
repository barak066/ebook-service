# -*- coding: utf-8 -*-

from . import Info

class ArticleInfo(Info):
    def __init__(self):
        self.magazine = ''
        self.title = ''
        self.link = ''
        self.year = None
        self.number = None
        self.category = ''
        self.authors = ''
        self.description = ''

    def _get_full(self):
        return [('Magazine' , self.magazine),
                ('Title' , self.title),
                ('Description' , self.description),
                ('Authors' , self.authors),
                ('Category' , self.category),
                ('Link' , self.link),
                ('Year' , self.year),
               ]


    def _get_short(self):
        return [ ('Title' , self.title),
                ('Link' , self.link),
               ]
        