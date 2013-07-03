# -*- coding: UTF-8 -*-
__author__ = 'pxanych'

import urllib
from lib.BeautifulSoup.BeautifulSoup import BeautifulSoup

def download_page(url):
    page = urllib.urlopen(url)
    try:
        code = page.getcode()
        url = page.geturl()
        info = page.info()
        content_type = info['content-type']
        if (content_type[:9] == 'text/html') or self._force:
            data = page.read()
            charset = page.headers.getparam('charset')
            if charset == 'windows-1251':
                data = data.decode('cp1251').encode('utf8')
        else:
            data = None
    finally:
        page.close()
        return url, code, info, data, BeautifulSoup(data)
