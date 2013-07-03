#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re

from server.book.models import Tag,Book, Author, BookFile, Language
from analyser import runners
from analyser.adds import logger
from server.django.db.models.query_utils import Q

def main(argv, **kwargs):
    prefix = 'db_'
    command, args = runners.get_command(kwargs['dir'], argv, prefix, 'db_to_text', lambda doc: eval(doc))
    if command:
        c = eval(prefix+command)
        c(args)


def db_get_libru_titles(*args):
    "get all titles from lib.ru with a suspicion on author containing"
    query = Q(pagelink__startswith='http://lib.ru')
    query = query & Q(title__contains='.')
    ex_query = Q(title__contains='...')
    books = Book.objects.filter(query).exclude(ex_query)
    for book in books:
        print book.title.encode('utf-8')
