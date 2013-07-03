import sys
# -*- coding: utf-8 -*-
import re
from classifier_settings import *
from book.models import *

def add_tag(t, book):
    if t == None or t.credit == 0 or t in book.tag.all():
        return False
    elif t.credit == -2:
        if t in book.tag.all():
            book.tag.remove(t)
            add_tag(t.parent, book)
            book.save()
            return True
        return False
    else:
        if t not in book.tag.all():
            book.tag.add(t)
            add_tag(t.parent, book)
            book.save()
            return True
        return False

tags = Tag.objects.all()
books = Book.objects.all()
print Book.objects.all().count()
n = 0;
for b in books:
    for t in b.tag.all():
        if t.credit != 0:
            if t.credit == -2:
                    b.tag.remove(t)
                    add_tag(t.parent, b)
                    b.save()
            else:
                    changed = add_tag(t.parent, b)
                    if changed:
                         b.save()
    n += 1
    if n % 1000 == 0:
        print n
