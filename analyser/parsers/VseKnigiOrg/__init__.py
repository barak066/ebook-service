# -*- coding: utf-8 -*-


"parser for site vse-knigi.org"

#TODO add sintax sugar (for instance,NeedHTML) for task setting

from tasks import InitialTask

class VseKnigiOrg:
    "site: vse-knigi.org"
    def __init__(self):
        self.site_link = 'http://vse-knigi.org/'
        self.initial_task = InitialTask( self.site_link)
    def get_filename(self):
        return r'vse_knigi_org'

