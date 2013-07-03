# -*- coding: UTF-8 -*-
__author__ = 'Павел'


from crawler import PageLoader, Ranker, Scheduler, ResultFilter, Results
from crawler.PageLoader import PageLoaderTask
from time import sleep
from os import environ
from KeyWords import KeyWords

environ['http_proxy'] = 'http://192.168.0.2:3128'

if __name__ == '__main__':

    KeyWords.load_link_kw();
    pl = PageLoader.PageLoader_v2()
    pl.add_task(PageLoaderTask('http://bookz.ru'))
    res = Results.Results()
    rf = ResultFilter.ResultFilter(res)
    rank = Ranker.Ranker(pl, rf)

    rank.active = True

    print 'now will exit'
