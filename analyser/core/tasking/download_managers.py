#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import urllib
import time
from urllib2 import HTTPError

from analyser.adds import logger
from . import BaseDownloadManager
from analyser.settings import TM_WAITING_TIME

"""
in this package:
implementations of DownloadManager
"""

class SimpleDownloadManager(BaseDownloadManager):
    def __init__(self):
        pass

    def download(self,link):
        page = self.downloading_page(link)
        data = self.read_data(page)
        page.close()
        return (data, page)

    def download_headers(self,link):
        page = self.downloading_page(link)
        return (page.headers, page)

    def downloading_page(self,link):
        try:
            page = self.get_page(link)
        except IOError:
            logger.write_fail("SimpleDM, IOError", link=link)
            raise IOError
        if page.getcode() != 200:
            logger.write_fail('SimpleDm, code is not 200', link=link, code=page.getcode())
        return page

    def read_data(self, page):
        return page.read()


class WaitingDM(SimpleDownloadManager):
    def download(self,link):
        page = self.downloading_page(link)
        data = self.read_data(page)
        page.close()
        return (data, page)

    def downloading_page(self,link):
        #TODO process case when link can't available to download  at all (NOW: it'll be loop trying to download
        downloaded = False
        while not downloaded:
            try:
                page = self.get_page(link)
            except HTTPError as http_error:
                logger.write_fail("WaitingDM, HTTPError", link=link)
                raise http_error
            except IOError:
                logger.write_fail("WaitingDM, IOError", link=link)
                self._delaying(TM_WAITING_TIME)
                continue
            if page.getcode() == 503:
                logger.write_fail('WaitingDM, code not 200, waiting', link=link, code=page.getcode())
                print 'Error 503,',
                self._delaying(TM_WAITING_TIME)
            else:
                downloaded = True
        return page
    
    def _delaying(self,sec):
        print 'waiting %d seconds...' % sec
        time.sleep(sec)


class ProxyDM(BaseDownloadManager):
    def __init__(self, *args):
        #super(ProxyDM,self).__init__(*args)
        self.opener = urllib.FancyURLopener()
        from analyser.settings import path_to_project
        self.proxies = file( os.path.join(path_to_project, 'analyser/data/proxies_list.txt') ).readlines()
        import random
        random.shuffle(self.proxies)
        self.change_proxy()
    def download(self,link):
        downloaded = False
        while not downloaded:
            try:
                page = self.opener.open(link)
            except IOError:
                logger.write_fail("ProxyDM, IOError", link=link)
                self.change_proxy()
                continue
            if page.getcode() == 503:
                logger.write_fail('ProxyDM, code is 503', link=link, code=page.getcode())
                self.change_proxy()
            else:
                downloaded = True
        data = self.read_data(page)
        page.close()
        return (data, page)

    def change_proxy(self):
        proxy = self.proxies.pop(0)
        self.proxies.append(proxy)
        msg = 'changing proxy on ' + proxy
        logger.write('ProxyDM',msg=msg)
        print msg
        schemes = ['http','https']
        for scheme in schemes:
            self.opener.proxies[scheme]="%s://%s" % (scheme, proxy)



class MagazinesDM(BaseDownloadManager):
    def download(self,link):
        opener = urllib.FancyURLopener()
        opener.addheader("Accept-Charset", "windows-1251")
        page = opener.open(link)
        data = self.read_data(page)
        page.close()
        return (data,page)
