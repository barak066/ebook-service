# -*- coding: utf-8 -*-

from tasks import InitialTask

#TODO add sintax sugar (for instance,NeedHTML) for task setting

class ZhurnalLibRu:
    "site: zhurnal.lib.ru"

    def __init__(self):
        #sitelink is not to main page, because of undefined HTML errors at main page
        self.site_link = 'http://zhurnal.lib.ru/janr/index_janr_11-1.shtml'
        self.initial_task = InitialTask( self.site_link)

    def get_filename(self):
        return r'zhurnal_libru'