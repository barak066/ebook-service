"""adds ebooks prefix to urls"""
from django.contrib import admin
from django.conf.urls.defaults import *

try:
    from settings import ROOT_URL
except ImportError:
    ROOT_URL = r''

from spec.logger import create_log

create_log()

admin.autodiscover()

urlpatterns = patterns('',
    (ROOT_URL, include('urls_root')),
)


