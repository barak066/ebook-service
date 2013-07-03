#!/usr/bin/python
__author__ = 'pxanych'

import os, time, hotshot
from sys import path
path.insert(0, '/home/pxanych/ebook-service')
os.environ['http_proxy'] = 'http://192.168.0.2:3128'
from crawler import ContentExtractor, PageLoader
from lib.BeautifulSoup import BeautifulSoup

if __name__ == '__main__':
    pl = PageLoader.PageLoader()
    pl.add_task(PageLoader.PageLoaderTask('http://bookz.ru'))
    time.sleep(4)
    result = pl.get_loaded_page()

    soup = BeautifulSoup.BeautifulSoup(result.data)

    cl = ContentExtractor.extract_mapped_content_list(soup.find('body'))

    print 'ok'

