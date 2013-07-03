# -*- coding: utf-8 -*-
from lib.BeautifulSoup.BeautifulSoup import BeautifulSoup
import urllib
from lib.chardet.universaldetector import UniversalDetector

def download_soup(link):
    page = urllib.urlopen( link )
    return get_soup( (page.read(), page) )


def get_text(html):
    data,page = html
    ud = UniversalDetector()
    ud.feed(data)
    ud.close()
    encoding = ud.result['encoding']
    data = unicode(data, encoding)
    return data

def get_soup(html):
    data, page = html
    charset = page.headers.getparam('charset')
    if charset:
        bs = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES,  fromEncoding=charset)
    else:
        bs = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    return bs
