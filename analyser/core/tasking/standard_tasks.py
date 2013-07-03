# -*- coding: utf-8 -*-

from analyser.core.db.booksaver import BooksToDatabase

from . import BaseTask

"""
in this package:
standard tasks, can be used by any parser
"""

BOOK_SAVER = BooksToDatabase()

class BookSavingTask(BaseTask):
    def __init__(self, book_info):
        BaseTask.__init__(self)
        self.book_info = book_info
        self.weight = -100
        self.longterm = True

    def __repr__(self):
        s = '<BookSavingTask: %s>' % self.book_info.simple_string()
        return s.encode('utf-8')

    def execute(self):
        BOOK_SAVER.save_books( [self.book_info] )
        return True

