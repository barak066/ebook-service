import sys
# -*- coding: utf-8 -*-
import re
try:
    from classifier_settings import *
except Exception:
    pass
from book.models import *

tags = Tag.objects.all()
for t in tags:
    if not (t.name == t.name.lower()):
        t.name = t.name.lower()
        t.save()
tags = Tag.objects.all().order_by("credit").reverse()
outp = open('taglist', 'w')
for t in tags:
    if Book.objects.filter(tag=t).count() > 9 or t.credit != 0:
        outp.write(t.name.encode('UTF-8'))
        outp.write('\n')
        outp.write(str(t.credit))
        outp.write('\n')
        if t.parent != None:
            outp.write(t.parent.name.encode('UTF-8'))
        else:
            outp.write("null")
        outp.write('\n****\n')
outp.close
