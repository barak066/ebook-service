# -*- coding: UTF-8 -*-
__author__ = 'pxanych'

import globalcrawersettings
from linkFunctions import get_netlock

class Results(object):

    def __init__(self, s_file = 'results'):
        self._settings_file = s_file
        self._settings = globalcrawersettings.load_settings(self._settings_file)
        self.sites = self._settings.get('sites', set())
        self.books = self._settings.get('books', set())

    def save_state(self):
        """
        Dumps current VisitHistory's state to disk.
        """
        self._settings['sites'] = self.sites
        self._settings['books'] = self.books
        globalcrawersettings.dump_settings(self._settings, self._settings_file)
        
    def submit_book_link(self, url, parent_page_url):
        self.books.add((url, parent_page_url))
        print 'Book link submitted'
        
    def submit_site(self, site_url):
        self.sites.add(site_url)
        print 'Site submitted ' + site_url + '    '

    def list_sites(self):
        roots = set(map(get_netlock, self.sites))
        roots = list(roots)
        for root in sorted(roots):
            print root + '\n'
