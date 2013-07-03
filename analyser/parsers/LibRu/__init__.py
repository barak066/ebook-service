# -*- coding: utf-8 -*-

import re
from datetime import datetime
import urllib
from analyser.adds import helpers
from analyser.adds import logger
from analyser.core.tasking.task_managers import DelayingSimpleTaskManager
from analyser.core.tasking.task_storages import TaskStorageDB
from server.django.db.models.query_utils import Q
from tasks import DirPage
from analyser.core.tasking.download_managers import WaitingDM
from server.analyser_app.models import Refresh
import analyser.settings

LAST_MODIFIED = 'LAST-MODIFIED'
class LibRu:
    "site: lib.ru"

    def __init__(self):
        self.site_link = 'http://lib.ru/'
        self.initial_task = DirPage( self.site_link )

    def get_filename(self):
        return r'libru'


class DM_LibRu(WaitingDM):
    #TODO add right processing of redirecting cases
    def bookfile_condition(self,url):
        return re.match(".+_Ascii.txt$",url)

    def read_data(self, page):
       if self.bookfile_condition(page.url):
           return page.read( analyser.settings.LIBRU_DEFINE_LANG_BY_BYTES )
       return WaitingDM.read_data(self,page)

class DM_LibRu_AddRefreshLinks(DM_LibRu):

    TIME_FORMAT = "%a, %d %b %Y %H:%M:%S %Z"
    def read_data(self, page):
        if not self.bookfile_condition(page.url):
            self.read_last_modified(page)
        return super(DM_LibRu_AddRefreshLinks,self).read_data(page)
    
    def read_last_modified(self,page):
        field = LAST_MODIFIED
        if not helpers.check_local_link('http://lib.ru', page.url):
            return
        if field in page.headers:
            new_date = datetime.strptime(page.headers[field], DM_LibRu_AddRefreshLinks.TIME_FORMAT )
            refreshes = Refresh.objects.filter(link=page.url)
            if refreshes:
                refreshes[0].last_modified = new_date
                refreshes[0].save()
            else:
                Refresh.objects.create(link=page.url, last_modified= new_date)

class TM_LibRu(DelayingSimpleTaskManager):
    "miss tasks with not-local url"
    def __init__(self, *args):
        super(TM_LibRu,self).__init__(*args)

    def tasks_executing_loop(self):
        task = self.storage.get_task()
        if task.need_html:
            print '    downloading: %s' % task.link
            if not helpers.check_local_link('http://lib.ru', task.link):
                logger.write('TM_LibRu: not local link!', notlocallink=task.link)
                self.storage.mark_executed()
                return
            page = (self.dm.download(task.link) , )
            url = page[0][1].url
            if not helpers.check_local_link('http://lib.ru', url):
                logger.write('TM_LibRu: not local link!', notlocallink=url,link=task.link)
                self.storage.mark_executed()
                return
        else:
            page = ()
        self.print_executing(task)
        self.execute_task(task, page)

class TM_LibRuRefresh(DelayingSimpleTaskManager):
    "executing tasks, checking LAST_MODIFIED header (miss if actual data)"
    def __init__(self, *args):
        super(TM_LibRuRefresh,self).__init__(*args)

    def tasks_executing_loop(self):
        task = self.storage.get_task()
        if task.need_html:
            print '    downloading: %s' % task.link
            headers, page = self.dm.download_headers(task.link)
            field = LAST_MODIFIED
            if field in headers:
                lm_date = datetime.strptime(headers[field], DM_LibRu_AddRefreshLinks.TIME_FORMAT )
                refreshes = Refresh.objects.filter(link=page.url)
                if refreshes and refreshes[0].last_modified == lm_date:
                    print 'link ', page.url, 'was scanned yet. Avoiding it...'
                    self.storage.mark_executed()
                    return                     
            page = (self.dm.download(task.link) , )
        else:
            page = ()
        self.print_executing(task)
        self.execute_task(task, page)



def refresh_libru():
    print 'scanning what should be refreshed...'
    refreshes = Refresh.objects.all()
    links = []
    ref_dm = WaitingDM()
    for refresh in refreshes:
        headers, page = ref_dm.download_headers(refresh.link)
        print refresh.link,
        field = LAST_MODIFIED
        if field in headers:
            new_date = headers[field]
            if refresh.check_refreshable(new_date):
                links.append( (refresh.link, new_date) )
                print '--> REFRESH',
        else:
            print ' no', field, 'in headers!',
        print 
    if not links:
        print 'nothing to refresh. Everything is up-to-date'

    parser = LibRu()
    parser_name = parser.get_filename()+'_refresh'
    storage = TaskStorageDB( parser_name, [],Q(parser_name=parser_name, good=True)  )

    for link, date in links:
        refresh = Refresh.objects.get(link=link)
        refresh.delete()
#TODO don't forget about make last-modified links actual
        # now actual is when it'll be updated by again scanning
#        refresh.last_modified = date
        task = DirPage(link)
        print 'adding task for refresh:', task
        storage.accept_new_tasks( [task] )

    dm = DM_LibRu_AddRefreshLinks()
    tm = TM_LibRuRefresh(storage, dm)
    tm.run()
    print 'refreshing is finished'
