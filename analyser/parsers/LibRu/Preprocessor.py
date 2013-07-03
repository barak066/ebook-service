# -*- coding: utf-8 -*-

import re
from analyser.core.info.BookInfo import BookInfo
from analyser.core.db.preprocessing import  preprocess_authors

class Preprocessor:

    @staticmethod
    def guess_lang_by_link(link):
        regexps = {'_engl.txt_Ascii.txt$' : 'en', \
                   '_germ.txt_Ascii.txt$' : 'de' }
        for regexp,lang in regexps.items():
            if re.search(regexp,link):
                return lang
        return '?'

    @staticmethod
    def cleanup_kilobytes(title):
        cleanups = ("(\(\s*[0-9]*\s*k\s*\))" ,
                    "(\(\s*\))",
                   )
        for cleanup in cleanups:
            title = Preprocessor.cleanup( title, cleanup )
        return title

    @staticmethod
    def cleanup_year(text):
        result =  Preprocessor.cleanup(text, "(\([0-9]{4}\))")
        result =  Preprocessor.cleanup(result, "(\[[0-9]{4}\])")
        return result

    @staticmethod
    def cleanup(text, pattern):
        match = re.search(pattern,text)
        if match:
            for group in match.groups():
                text = text.replace(group, '')
        return text

    @staticmethod
    def get_authors(text):
        points =  text.split('. ')
        if len(points) > 1:
            return [ points[0] ]
        return []

    @staticmethod
    def is_author(text):
        filters = [ u"^[А-Яа-я]{1,2}\.\s?[А-Яа-я]{1,2}\.\s?[A-Яа-я-]+" ,
                    u"^[А-Я]\.\s*[А-Я][A-Яа-я-]+$" ,
                    u"^[А-Я][а-я]\.\s*[А-Я][A-Яа-я-]+$" ,
                    u"^[А-Яа-я]+\s+[А-Я][А-Яа-я]+$",
                    u"^[А-Я][а-я]+\s+[А-Я][а-я]+\s+[А-Я][а-я]+$",
                  ]
        exclusions = [ u'Речь' ]
        if any ( re.search('%s' % exclusion, text) for exclusion in exclusions) :
            return False
        for _, filter in enumerate(filters):
            if re.match( filter, text):
                return True
        return False

    @staticmethod
    def cleanup_comma(author):
        "clean up comma sign in authors name like this; Asprin, Robert (example page http://lib.ru/INOFANT/)"
        return author.replace(',', ' ')

    @staticmethod
    def cleanup_numeration(title):
        title = title.strip()
        pattern = '^([0-9]+\\.).+'
        m = re.match(pattern, title)
        if m:
            title = title.replace(m.groups()[0], '').strip()
        return title

    @staticmethod
    def extract_authors(title):
        return_authors = []
        authors = Preprocessor.get_authors(title)
        authors = preprocess_authors( authors )
        for author in authors:
            if Preprocessor.is_author(author):
                return_authors.append(author)
        for author in return_authors:
            title = title.replace(author, '')
        title = title.lstrip('.').strip()
        return return_authors, title

