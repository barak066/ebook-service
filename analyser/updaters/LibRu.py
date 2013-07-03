#!/usr/bin/env python
# -*- coding: utf-8 -*-
from analyser.parsers.LibRu.tasks import Preprocess

from server.book.models import Book,Author
from server.django.db.models.query_utils import Q
from analyser.core.tasking.standart_tasks import standart_tasks
from analyser.parsers.LibRu.Retriever import Retriever
from analyser.core.db.preprocessing import preprocess_title
from analyser.core.db.booksaver import get_bookinfo_from_db




class InitialTask(standart_tasks):
    def __init__(self):
        standart_tasks.__init__(self)
    def __repr__(self):
        return '<InitialTask libru updater>'
    def execute(self):
        query = Q(pagelink__startswith="http://lib.ru")
        #query = query & ( Q(title__contains=')') | Q(title__contains='_') )
        query = query & Q(title__contains='.')
        exclude_q = Q( title__contains='...')
        books = Book.objects.filter(query).exclude(exclude_q)
        self.tasks = [ TitleProcess(book.id) for book in books ]
        return True


class InitialUpdaterTask(standart_tasks):
    def __init__(self, books):
        standart_tasks.__init__(self)
        self.books = books
    def __repr__(self):
        return '<InitialUpdaterTask Libru>'
    def execute(self):
        bookinfos = [ get_bookinfo_from_db(book.id) for book in self.books ]
        self.tasks = [ Preprocess( bookinfo) for bookinfo in bookinfos ]
        return True

class TitleProcess(standart_tasks):
    def __init__(self, book_id):
        standart_tasks.__init__(self)
        self.book_id=book_id
        self.longterm = True
        self.weight = 10
    def __repr__(self):
        return '<TitleProcess: %d>' % self.book_id
    def execute(self):
        book = Book.objects.get(id=self.book_id)
        title = Retriever.cleanup_kilobytes(book.title)
        title = preprocess_title(title)

        new_authors, new_title = Retriever.extract_authors(title)
        if new_authors:
            title = new_title
            authors = [ Author.objects.get_or_create(name=author)[0] for author in new_authors]
            book.author = authors
        else:
            authors = book.author.all()

        title = preprocess_title(title)
        if book.title != title:
            print "%d %s : '%s' %s=> %s : '%s'" % ( book.id,
                                                " % ".join([a.name.encode('utf-8') for a in book.author.all() ] ),
                                                book.title.encode('utf-8'),
                                               "="*(3 if new_authors else 0),
                                                 " % ".join([a.name.encode('utf-8') for a in authors ] ),
                                                title.encode('utf-8'),
                                              )

        book.title = title
        book.credit = 1
        book.save()
        return True
