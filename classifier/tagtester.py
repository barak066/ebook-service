import sys
# -*- coding: utf-8 -*-
import re
try:
    from classifier_settings import *
except Exception:
    pass
from book.models import *
from server.django.db.models.query_utils import Q

tags2 = Tag.objects.filter(credit=2)
for t in tags2:
    print t.name
print
tags1 = Tag.objects.filter(credit=1)
for t in tags1:
    print t.name + ': ' + t.parent.name
print
tags3 = Tag.objects.filter(Q(credit=2) |  Q(credit=1))
for t in tags3:
    print t.name
