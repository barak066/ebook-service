# -*- coding: UTF-8 -*-
__author__ = 'pxanych'

from crawler.tests.scratch_functions import download_page
from crawler.rankFunctions import compare_pages

if __name__ == '__main__':
    r1 = download_page('http://flibusta.net')
    r2 = download_page('http://ozon.ru')

    bs1 = r1[4].find('body')
    bs2 = r2[4].find('body')

    print(compare_pages(bs1, bs2))
