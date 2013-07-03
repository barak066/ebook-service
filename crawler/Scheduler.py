# -*- coding: UTF-8 -*-
__author__ = 'pxanych'

from crawler.PageLoader import PageLoaderTask
from crawler.LinkQueue import LinkQueue
from crawler.linkFunctions import get_netlock
from crawler import globalcrawersettings
from threading import Timer, Lock
import types


class Scheduler(object):

    def __init__(self, page_loader, result_filter, ranker, visit_history, site_crawl_quota = 40):
        self._page_loader = page_loader
        self._result_filter = result_filter
        self._ranker = ranker
        self._ranker._scheduler = self
        self._visit_history = visit_history
        self._site_crawl_quota = site_crawl_quota
        self._main_proc_timer = None
        self._load_state()
        #self._current_site_queue = LinkQueue(site_crawl_quota)
        #self._future_site_queue = LinkQueue(1000)
        #self._stage_ttl = site_crawl_quota
        #self._current_site = ''
        #self._filtered_links = []
        #self._page_url = ''
        self.__active = False
        self._lock_run = Lock()

    def ready_to_shutdown(self):
        return self._page_loader.ready_to_shutdown() \
               and self._ranker.ready_to_shutdown() \
               and self._result_filter.ready_to_shutdown()

    def _load_state(self):
        settings = globalcrawersettings.load_settings('scheduler')
        self._stage_ttl = settings.get('_state_ttl', self._site_crawl_quota)
        self._current_site = settings.get('_current_site', '')
        self._filtered_links = settings.get('_filtered_links', [])
        self._page_url = settings.get('_page_url', '')
        self._future_site_queue = settings.get('_future_site_queue', LinkQueue(1000))
        self._current_site_queue = settings.get('_current_site_queue', LinkQueue(self._site_crawl_quota))

    def save_state(self):
        settings = dict()
        settings['_state_ttl'] = self._stage_ttl
        settings['_current_site'] = self._current_site
        settings['_filtered_links'] = self._filtered_links
        settings['_page_url'] = self._page_url
        settings['_future_site_queue'] = self._future_site_queue
        settings['_current_site_queue'] = self._current_site_queue
        globalcrawersettings.dump_settings(settings, 'scheduler')

    def _get_active(self):
        """active property getter"""
        self._lock_run.acquire()
        ret_value = self.__active
        self._lock_run.release()
        return ret_value

    def _set_active(self, state):
        """active property setter"""
        if type(state) != types.BooleanType:
            raise TypeError('state should be boolean')
        self._lock_run.acquire()
        old_active = self.__active
        self.__active = state
        if not old_active:
            self._main_proc_timer = Timer(1, self._main_proc)
            self._main_proc_timer.start()
        self._lock_run.release()

    def _main_proc(self):
        """
        Main procedure:
        get [(link_url, weight)] from ResultFilter and pass best links to PageLoader
        """
        if self._stage_ttl >= 0: #main stage
            #fill queues:
            match_function = lambda x: get_netlock(x.user_data) == self._current_site or self._current_site == ''
            res = self._result_filter.get_result(match_function)
            if res:
                page_url, weight, filtered_links = res
                if not self._current_site:
                    self._current_site = get_netlock(page_url)
                self._visit_history.set_visited(page_url, weight)
                for link, weight in filtered_links:
                    netloc = get_netlock(link)
                    if netloc == self._current_site:
                        if self._visit_history.is_visited(link):
                            continue
                        self._current_site_queue.put((weight,link), True)
                    else:
                        if netloc != self._current_site and self._visit_history.is_visited_site(link):
                            continue
                        self._future_site_queue.put((weight,link), True)
            #assign PL tasks
            while self._page_loader.have_slots() and not self._current_site_queue.is_empty():
                task = PageLoaderTask(self._current_site_queue.get())
                self._page_loader.add_task(task)
        #
        if self._stage_ttl < 0: #switching stages
            self._page_loader.purge_tasks(lambda x: x.user_data != self._current_site)
            self._ranker.purge_tasks(lambda x: get_netlock(x.user_data) != self._current_site)
            self._result_filter.purge_tasks(lambda x: get_netlock(x.user_data) != self._current_site)
            best_nl = self._max_avg_weight(self._future_site_queue)
            if best_nl:
                filter_function = lambda x: get_netlock(x[1]) != best_nl
                self._current_site = best_nl
                self._current_site_queue._queue = self._future_site_queue.filter(filter_function)
            self._stage_ttl = self._site_crawl_quota
        #
        self._continue_work(1)

    def _continue_work(self, sleep_time):
        """
        Restarts _main_proc and switches stages, if needed
        """
        self._lock_run.acquire()
        self._stage_ttl -= 1
        if self.__active:
            self._main_proc_timer = Timer(sleep_time, self._main_proc)
            self._main_proc_timer.start()
        self._lock_run.release()

    def _max_avg_weight(self, link_queue):
        """
        Returns netloc of the site, which has the highest average weight.
        """
        weights = {}
        for w,l in link_queue._queue:
            netloc = get_netlock(l)
            sum_w, count = weights.get(netloc, (0, 0))
            weights[netloc] = sum_w + w, count + 1
        max_aw = None
        best = None
        t = None
        try:
            for t in weights.items():
                nl, (sum_w, count) = t
                if sum_w / count > max_aw:
                    max_aw = sum_w / count
                    best = nl
        except Exception:
            print 'fail'
        return best

    def set_accepted_site(self):
        pass    
        
    active = property(_get_active, _set_active)

