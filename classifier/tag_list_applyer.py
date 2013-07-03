import sys
# -*- coding: utf-8 -*-
import re
from classifier_settings import *
from book.models import *

inp=open('taglist', 'r')
genrelist = inp.read()
genrelist = unicode(genrelist.decode('UTF-8')).lower()
splitter = re.compile('''\*\*\*\*\n''', re.U)
raw_genres = (splitter.split(genrelist))[0:-1]
for rg in raw_genres:
    splitter = re.compile('''\n''', re.U)
    raw_data = (splitter.split(rg))
    tag, created = Tag.objects.get_or_create(name=raw_data[0])
    changed = False
    credit = int(raw_data[1])
    if credit != tag.credit:
        tag.credit = credit
        changed = True
    if raw_data[2] != 'null':
        parent, created = Tag.objects.get_or_create(name=raw_data[2])
        if parent != tag.parent:
            tag.parent = parent
            changed = True
    else:
        parent = None
        if parent != tag.parent:
            tag.parent = parent
            changed = True
    if changed:
        tag.save()
