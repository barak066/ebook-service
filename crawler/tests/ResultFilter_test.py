# -*- coding: UTF-8 -*-
__author__ = 'pxanych'

from crawler.ResultFilter import ResultFilter
from crawler.PageLoader import PageLoader_v2, PageLoaderTask
from crawler.Ranker import Ranker
from crawler.Results import Results
from time import sleep
from os import environ
from crawler import linkFunctions

environ['http_proxy'] = 'http://192.168.0.2:3128'

if __name__ == '__main__':
    pl = PageLoader_v2()
    pl.add_task(PageLoaderTask('http://bookz.ru'))

    r = Results()

    rf = ResultFilter(r)

    ranker = Ranker(pl,rf)
    ranker.active = True

    sleep(10)
    t = rf.get_links(10)
    ret = t[0]
    print 'finished'