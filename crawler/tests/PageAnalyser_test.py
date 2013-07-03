__author__ = 'pxanych'

from crawler import PageLoader
from crawler.PageLoader import PageLoaderTask
from crawler.PageAnalyser2 import PageAnalyser
from time import sleep
from os import environ

environ['http_proxy'] = 'http://192.168.0.2:3128'

if __name__ == '__main__':
    pl = PageLoader.PageLoader_v2()
    pl.add_task(PageLoaderTask('http://bookz.ru'))

    sleep(2)
    
    page = None
    while True:
        page = pl.get_loaded_page()
        if page:
            break
        sleep(1)

    pa = PageAnalyser(page)
    pa.get_page_weight()

    print pa.get_page_weight()
