#!/usr/bin/env python
# -*- coding: utf-8 -*-

from analyser.adds.OpenerHolder import OpenerHolder
from lib.BeautifulSoup.BeautifulSoup import BeautifulSoup
from analyser.adds import logger
from server.book.models import Book, BookFile, Annotation
from analyser.core.tasking.standart_tasks import standart_tasks


class RemoveAnnotationTask(standart_tasks):
    def __init__(self, id):
        standart_tasks.__init__(self)
        self.weight = 10
        self.id = id
    def __repr__(self):
        return '<RemoveAnnotationTask: %s>' % self.id
    def execute(self):
        book = Book.objects.get(pagelink='http://flibusta.net/b/%s'  % self.id)
        book.annotation_set.all().delete()
        return True

class GetBookFileTypeEmpty(standart_tasks):
    def __init__(self):
        standart_tasks.__init__(self)
        self.weight = -5
    def __repr__(self):
        return '<GetBookFileTypeEmpty>'
    def execute(self):
        bookfiles = BookFile.objects.filter(type="", link__contains="flibusta.net")
        self.tasks = [BookFileTyper(bookfile.id) for bookfile in bookfiles]
        return True

class BookFileTyper(standart_tasks):
    def __init__(self, id):
        standart_tasks.__init__(self)
        self.weight = -5
        self.id = id
    def __repr__(self):
        return '<BookFileTyper: %s>' % self.id
    def execute(self):
        bookfile = BookFile.objects.get(id=self.id)
        bookfile.type = Retriever.recognize_type(bookfile.link)
        bookfile.save()
        return True

class InitialGetAnnotation(standart_tasks):
    def __init__(self):
        standart_tasks.__init__(self)
        self.weight = 10
    def __repr__(self):
        return '<InitialGetAnnotation:>'
    def execute(self):
        books = Book.objects.filter(pagelink__contains="flibusta.net", annotation__isnull=True, lang='ru')
        self.tasks = [ GetAnnotation(book.id,book.pagelink) for book in books ]
        return True


class GetAnnotation(standart_tasks):
    def __init__(self, id, pagelink):
        standart_tasks.__init__(self)
        self.weight = 10
        self.link = pagelink
        self.need_html = True
        self.id = id
    def __repr__(self):
        return '<GetAnnotation: book# %s, %s>' % (self.id, self.link)
    def execute(self,html):
        data, page = html
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES )
        summary = Retriever.get_summary(soup)
        if summary:
            self.tasks = [ SummarySaver(self.id,unicode(summary)) ]
        return True

class SummarySaver(standart_tasks):
    def __init__(self, id, summary):
        standart_tasks.__init__(self)
        self.weight = 10
        self.id = id
        self.longterm = True
        self.summary = summary
    def __repr__(self):
        return '<SummarySaver: book#%s>' % self.id
    def execute(self):
        logger.write_success('saved summary for book', id=self.id)
        book = Book.objects.get(id=self.id)
        Annotation.objects.create(name=self.summary, book=book)
        return True


import analyser.settings
FLIBUSTA_USER = getattr(analyser.settings, 'FLIBUSTA_USER', 'user')
FLIBUSTA_PASS = getattr(analyser.settings, 'FLIBUSTA_PASS', 'pass')
site_link ='http://flibusta.net'
auth_data = {'name' : FLIBUSTA_USER, \
             'pass' : FLIBUSTA_PASS, \
             'persistent_login' : '1', \
             'form_id' : 'user_login_block'
            }
OPENER = OpenerHolder(auth_data, site_link)

def routine(self, args):
    "Page loading routine for Fibusta.net"
    page = OPENER.urlopen(self.user_data.link)
    data = page.read()
    page.close()
    self.result = { 'task'    : self.user_data,
                    'headers' : page.headers,
                    'data'    : data,
                    'page'    : page,
                  }
    self.complete = True
