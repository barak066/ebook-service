# -*- coding: utf-8 -*-

"""saves loaded pages on disk and returns them"""
import urllib
import os
import re
import urlparse



import analyser.settings

CACHE_FOLDER = getattr(analyser.settings, 'CACHE_FOLDER')

class Cacher():
    def __init__(self, urlopener):
        self._urlopener = urlopener
        if not os.path.exists(CACHE_FOLDER):
            os.makedirs(CACHE_FOLDER)
    def urlopen(self,link):
        hash = Cacher.link_hasher(link)
        if not os.path.exists( os.path.join(CACHE_FOLDER,hash)):
            self.download(link)
        f = open(CACHE_FOLDER+hash,'r')
        return f

    @staticmethod
    def link_hasher(link):
        scheme, netloc, url, params, query, fragment = urlparse.urlparse(link)
        name = netloc + url
        name = name.replace('-','_').replace('/','_').replace('.','_')
        return name

    def download(self,link):
        print 'downloading'
        hash = Cacher.link_hasher(link)
        html = self._urlopener.urlopen(link)
        f = open(CACHE_FOLDER+hash,'w')
        f.write(html.read())
        f.close()
        
