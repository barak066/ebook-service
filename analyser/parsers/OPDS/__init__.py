# -*- coding: utf-8 -*-

from tasks import Page
from analyser.adds import helpers
from lib.BeautifulSoup.BeautifulSoup import BeautifulStoneSoup

#TODO add sintax sugar (for instance,NeedHTML) for task setting

class OPDS:
    "OPDS parser"

    def __init__(self, opds_link):
        self.opds_link = opds_link
        self.initial_task = Page( self.opds_link )

    def get_soup(self,data):
        return BeautifulStoneSoup(data, convertEntities="xml")

    def get_filename(self):
        site_link = helpers.get_site_root_link(self.opds_link)
        site_link = site_link.replace('http://','')
        site_link = site_link.replace('www.','')
        site_link = site_link.replace('.','_')
        return site_link