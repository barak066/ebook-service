# -*- coding: UTF-8 -*-
__author__ = 'Павел'

from Worker import Worker
from WorkerTask import WorkerTask
from PageAnalyser2 import PageAnalyser
from threading import Lock, Timer
import types

class Ranker(object):

    def __init__(self, page_loager, result_filter):
        self._rank_worker = Worker()
        self._page_loader = page_loager
        self._result_filter = result_filter
        self._main_proc_timer = None
        self.__active = False
        self._lock_run = Lock()
        self._shutting_down = False

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

    def ready_to_shutdown(self):
        return self._page_loader.ready_to_shutdown() and self._rank_worker.ready_to_shutdown()

    def purge_tasks(self, filter_not_match):
        self._rank_worker.purge_tasks(filter_not_match)

    def _main_proc(self):
        """
        Main procedure:
        get page from PageLoader, rank it and give it to ResultFilter
        """
        sleep_time = 1
        page_result = self._page_loader.get_loaded_page()
        #page_result is namedtuple('url, code, info, data, user_data')
        if page_result:
            if page_result.data:
                rw_task = WorkerTask(page_result, ranker_routine, page_result[0])
                self._rank_worker.add_task(rw_task)
            sleep_time = 0
        else:
            pass#self._result_filter.thresholds[1] -= 1
        rw_completed_task = self._rank_worker.get_completed_task()
        if rw_completed_task:
            self._result_filter.submit_ranker_result(rw_completed_task.result)
            sleep_time = 0
            #print 'Completed!'
        self._lock_run.acquire()
        if self.__active:
            self._main_proc_timer = Timer(sleep_time, self._main_proc)
            self._main_proc_timer.start()
        self._lock_run.release()

    active = property(_get_active, _set_active)


def ranker_routine(self, args):
    """
    This function is passed to Ranker's Worker class.
    args is:
        namedtuple('url, code, info, data, user_data')
    """
    analyser = PageAnalyser(args)
    self.result.append(analyser.page_url)
    self.result.append(analyser.get_page_weight())
    self.result.append(analyser.weight_links(1))     #1 is the window width
    self.complete = True
