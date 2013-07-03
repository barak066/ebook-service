# -*- coding: utf-8 -*-

import re


class Preprocessor:

    REPLACES = { u"╚" : u"\"",
                 u"╩" : u"\"",
                 u"╗" : u"i",
                 u"√"  : u"\u2014",
                 u"≈"  : u"—",
                 u"╟" : u"o",
                 u"┘" : u"...",
                 u"╧"  : u"№",
                 u"⌠"  : u"\"",
                 u"■"  : u"\"",
            }

    @staticmethod
    def change_strange_symbols(string):
        if string:
            for what, to in Preprocessor.REPLACES.items():
                string = string.replace(what,to)
        return string

    @staticmethod
    def magazine_info(info):
        info.about = Preprocessor.change_strange_symbols( info.about )
        info.name = Preprocessor.change_strange_symbols( info.name )
        info.description = Preprocessor.change_strange_symbols( info.description )

    @staticmethod
    def article_info(info):
        info.magazine = Preprocessor.change_strange_symbols( info.magazine )
        info.authors = Preprocessor.change_strange_symbols( info.authors )
        info.title = Preprocessor.change_strange_symbols( info.title )
        info.category = Preprocessor.change_strange_symbols( info.category )
        info.description = Preprocessor.change_strange_symbols( info.description )




