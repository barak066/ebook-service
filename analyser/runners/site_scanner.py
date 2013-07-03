#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import urlparse
import getopt

from analyser.parsers.FlibustaNet import FlibustaNet, AuthDM
#from analyser.parsers.LibRu import LibRu, LibRuDM #, LibRuDM_Refresher
from analyser.parsers.LibRu import LibRu, DM_LibRu, DM_LibRu_AddRefreshLinks, TM_LibRuRefresh, refresh_libru, TM_LibRu
from analyser.parsers.ZhurnalLibRu import ZhurnalLibRu
from analyser.parsers.OPDS import OPDS
from analyser.parsers.NehudlitRu import NehudlitRu
from analyser.parsers.Magazines import Magazines
from analyser.parsers.VseKnigiOrg import VseKnigiOrg

from analyser.core.tasking.task_managers import SimpleTaskManager, DelayingSimpleTaskManager
from analyser.core.tasking.download_managers import SimpleDownloadManager, MagazinesDM, WaitingDM, ProxyDM

from analyser.core.tasking.task_storages import TaskStorageDB
from server.analyser_app.models import Refresh
from server.django.db.models import Q

import analyser.settings
from server.django.db.models.query_utils import Q

def main(argv, **kwargs):

    opts, argv = getopt.getopt(argv, "",['rerun','refresh'])
    rerun,refresh = False,False
    for opt,value in opts:
        if opt=='--rerun':
            rerun = True
        if opt=='--refresh':
            refresh = True

    SITES =  (
            ( 'http://lib.ru', get_libru ),
            ( 'http://magazines.russ.ru', get_magazines ),
            ( 'http://nehudlit.ru', get_nehudlit ),
            ( 'http://data.fbreader.org', get_fbreader ),
            #( 'http://81.1.213.130:8091', get_flibusta_opds  ),
            ( 'http://vse-knigi.org', get_vseknigi_org ),
            ( 'http://flibusta.net', get_flibusta ),
            ( 'http://manybooks.net', get_manybooks ),
            ( 'http://smashwords.com', get_smashwords ),
            ( 'http://www.feedbooks.com', get_feedbooks ),
         )


    if argv:
        func,site = get_run_func( argv[0], SITES)
        if not func:
            print "site '%s' are not available for scanning" % site
    if not argv or not func:
        show_help()
        show_sites(SITES)
        sys.exit(0)
    if refresh and site != 'http://lib.ru':
        print 'refreshing is available only for lib.ru now. \nTo refresh other sites, you can rerun scanner for them.'
        print 'fot this, type: site_scanner --rerun <site_name>'
        sys.exit(0)
    if refresh and site=='http://lib.ru':
        refresh_libru()
        sys.exit(0)
    print 'running scanner for site', site
    if rerun and site == 'http://lib.ru':
        Refresh.objects.all().delete()
    if site == 'http://lib.ru':
        storage, dm = func()
        run_libru(storage,dm,rerun)
        sys.exit(0)
    run_scanning( func, rerun )

def run_scanning( func, rerun=False ):
    storage, dm = func()
    run_tm(storage,dm,rerun)

def show_help():
    print 'USAGE: site_scanner [--rerun]|[--refresh] <site_to_scan>'
    print 'example:  site_scanner http://lib.ru  -- scanning lib.ru site'
    print '          site_scanner --rerun nehudlit.ru  -- rescanning nehudlit.ru site'
    print '(note: refreshing is available only for lib.ru)'
    print

def show_sites(sites):
    print 'following sites are available to scan:'
    for site, func in sites:
        print " * %s" % site

def get_run_func( command, sites ):
    for site, func in sites:
        if convert_sitename(command) == convert_sitename(site):
            return func, site
    return None, command

def convert_sitename(sitename):
    sitename = sitename.lower()
    scheme, netloc, url, params, query, fragment = urlparse.urlparse(sitename)
    if scheme:
        sitename = netloc
    sitename = sitename.replace('.','').strip()
    return sitename

def run_tm(storage, dm, rerun=False):
    if rerun:
        print 'rerunning scanning...'
        storage.re_run()
    tm = DelayingSimpleTaskManager(storage, dm)
    tm.run()

def run_libru(storage,dm,rerun=False):
    if rerun:
        print 'rerunning scanning...'
        storage.re_run()
    tm = TM_LibRu(storage, dm)
    tm.run()

def get_storage_and_dm(parser):
    return ( get_storage(parser), WaitingDM() )

def get_storage(parser):
    parser_name = parser.get_filename()
    storage = TaskStorageDB( parser_name, [parser.initial_task],Q(parser_name=parser_name, good=True)  )
    return storage

def get_magazines():
    return ( get_storage(Magazines()), MagazinesDM() )

def get_libru():
    return  (get_storage(LibRu()), DM_LibRu_AddRefreshLinks() )

def get_flibusta():
    FLIBUSTA_PASS =  analyser.settings.FLIBUSTA_PASS
    FLIBUSTA_USER=  analyser.settings.FLIBUSTA_USER
    parser = FlibustaNet()
    if FLIBUSTA_PASS == 'xxx' and FLIBUSTA_USER == 'xxx':
        print "WARNING! You didn't set password and user for parsing flibusta.net. Some pages will be not available and their parsing will be incorrect!"
        dm = WaitingDM()
    else:
        data = parser.generate_auth_data(FLIBUSTA_USER,FLIBUSTA_PASS)
        dm = AuthDM(parser.site_link, data)
    return  (get_storage(parser), dm )
    
def get_fbreader():
    return  get_storage_and_dm( OPDS('http://data.fbreader.org/catalogs/litres/authors.php') )
def get_flibusta_opds():
    return  get_storage_and_dm( OPDS('http://81.1.213.130:8091/opds ') )
def get_manybooks():
    return  get_storage_and_dm( OPDS('http://www.manybooks.net/opds/titles.php') )
def get_smashwords():
    return  get_storage_and_dm(  OPDS('http://www.smashwords.com/atom/authors/alphabetic/_/epub/any') )
def get_feedbooks():
    return  get_storage_and_dm(  OPDS('http://www.feedbooks.com/discover/languages.atom') )
def get_zhurnal_libru():
    return  get_storage_and_dm(   ZhurnalLibRu() )
def get_nehudlit():
    return  get_storage_and_dm(  NehudlitRu() )
def get_vseknigi_org():
    return  get_storage_and_dm(  VseKnigiOrg() )

