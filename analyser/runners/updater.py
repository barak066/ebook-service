#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
from zipfile import ZipFile

from server.book.models import Tag,Book, Author, BookFile, Language
from analyser import runners



def main(argv, **kwargs):
    prefix = 'updater_'
    command,_ = runners.get_command(kwargs['dir'], argv, prefix, 'updater', lambda doc: eval(doc))
    if command:
        c = eval(prefix+command)
        c()

def get_first_not_none(iterable):
    for i in iterable:
        if i:
            return i
    return None



def updater_test():
    print 'hello world'


def updater_show_sorted_tags():
    tags = Tag.objects.all()
    tagnames = [tag.name for tag in tags]
    tagnames.sort()
    for tagname in tagnames:
        print tagname.encode('utf-8')

def check_integrity(new_tag, tag):
    try:
        another_tag = Tag.objects.get(name=new_tag)
    except Tag.DoesNotExist:
        return True
    books = Book.objects.filter(tag__name=tag.name)
    for book in books:
        print 'FIXED', new_tag, book.id, book.title
        tags = book.tag.all()
        t = [tag for tag in tags]
        if another_tag not in t:
            t.append( another_tag )
        book.tag = t
        book.save()
    return False


def updater_clean_not_actual():
    from server.book.models import Book, Author
    authors = Author.objects.filter(book__isnull=True)
    books = Book.objects.filter(book_file__isnull=True)
    n_authors = len(authors)
    print 'deleting authors with no books... (%d)' % n_authors
    authors.delete()
    n_books = len(books)
    print 'deleting books with no bookfiles... (%d)' % n_books
    books.delete()


    
