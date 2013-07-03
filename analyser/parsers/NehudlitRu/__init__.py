# -*- coding: utf-8 -*-

from tasks import InitialTask

#TODO add sintax sugar (for instance,NeedHTML) for task setting

class NehudlitRu:
    "site: nehudlit.ru"
    def __init__(self):
        self.site_link = 'http://nehudlit.ru/books/index.php'
        self.initial_task = InitialTask( self.site_link)

    def get_filename(self):
        return r'nehudlit_ru'
