# -*- coding: utf-8 -*-
import urllib
from tasks import InitialTask

#TODO add sintax sugar (for instance,NeedHTML) for task setting

class Magazines:
    "site: lib.ru"

    def __init__(self):
        self.site_link = 'http://magazines.russ.ru/'
        self.initial_task = InitialTask( self.site_link )

    def get_filename(self):
        return r'magazines'

def routine(self, args):
    opener = urllib.FancyURLopener()
    opener.addheader("Accept-Charset", "windows-1251")
    page = opener.open(self.user_data.link)
    data = page.read()
    page.close()
    self.result = { 'task'    : self.user_data,
                    'headers' : page.headers,
                    'data'    : data,
                    'page'    : page,
                  }
    self.complete = True