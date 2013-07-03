try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

import urllib
import urlparse
import re
from urllib import quote

from django.db import models
from django.contrib import admin
from djangosphinx.models import SphinxSearch
from djangosphinx.apis.current import SPH_MATCH_ANY
from django.core.files import File
from django.conf import settings


from spec.langcode import LANG_CODE

NAME_LENGTH = 255
LINK_LENGTH = 4000
TEXT_LENGTH = 10000

class AuthorAlias(models.Model):
    name = models.CharField(max_length=NAME_LENGTH, unique=True)

class Author(models.Model):
    alias = models.OneToOneField(AuthorAlias, null=True, blank=True)
