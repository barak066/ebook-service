"""
Module contains classes that are used for thread-safe page downloading
"""
import threading

__author__ = 'pxanych'

from linkFunctions import URLParser, get_netlock
from threading import  Lock
from collections import namedtuple
from globalcrawersettings import load_settings, dump_settings
from time import sleep
import types
import urllib

result_class = namedtuple('result', 'url, code, info, data, user_data')

class PageLoaderTask(object):
    """
    This class used to represent page loading task
    """
    def __init__(self, url, site = None, force_nonhtml_pages_loading = False, user_data = None):
        self._lock_complete = Lock()
        self.__complete = False
        self.gathered = False
        self.url = url
        self.user_data = get_netlock(url)
        self.result = None
        self.thread = None
        self._force = force_nonhtml_pages_loading
        if not site:
            self.site = URLParser(url).get_netloc()
        else:
            self.site = site
        return

    def _get_complete(self):
        """complete property getter"""
        self._lock_complete.acquire()
        complete = self.__complete
        self._lock_complete.release()
        return complete

    def _set_complete(self, state):
        """complete property setter"""
        if type(state) != types.BooleanType:
            raise TypeError('state should be boolean')
        self._lock_complete.acquire()
        self.__complete = state
        self._lock_complete.release()

    def routine(self):
        """
        Page loading routine
        """
        page = urllib.urlopen(self.url)
        try:
            code = page.getcode()
            url = page.geturl()
            info = page.info()
            content_type = info['content-type']
            if (content_type[:9] == 'text/html') or self._force:
                data = page.read()
                charset = page.headers.getparam('charset')
                if charset == 'windows-1251':
                    pass #data = data.decode('cp1251').encode('utf8')
            else:
                data = None
        finally:
            page.close()
            self.result = result_class(url, code, info, data, self.user_data)
            self.complete = True

    complete = property(_get_complete, _set_complete)



class PageLoader_v2(object):
    """
    Does all page downloading.
    Tasks are started in the order of their assignment.
    """
    def __init__(self):
        self._completed_tasks = []
        self._active_tasks = []
        self._scheduled_tasks = []
        self._lock_sched = threading.Lock()
        self._lock_compl = threading.Lock()
        self._lock_act = threading.Lock()
        self._lock_run = threading.Lock()
        self._running = False
        self._active = True
        self._main_proc_timer = None
        self._max_active_tasks = 16
        self._max_scheduled_tasks = 128
        self._load_state()

    def save_state(self):
        settings = dict()
        future_tasks = []
        for task in self._scheduled_tasks:
            future_tasks.append(task.url)
        settings['future_tasks'] = future_tasks
        dump_settings(settings, 'PageLoader')

    def _load_state(self):
        settings = load_settings('PageLoader')
        future_tasks = settings.get('future_tasks', [])
        for url in future_tasks:
            self._scheduled_tasks.append(PageLoaderTask(url))
            
    def enter_sleep_mode(self):
        self._active = False
        while len(self._active_tasks) + len(self._completed_tasks):
            sleep(1)

    def wake_up(self):
        self._active = True
        self.activate()

    def ready_to_shutdown(self):
        l_a = len(self._active_tasks)
        l_c = len(self._completed_tasks)
        return l_a + l_c == 0

    def _main_proc(self):
        """
        while have tasks: do some work
        """
        self._gather_completed_tasks()
        if self._active:
            self._activate_tasks()
        #if have more job to do - wait for 1 second and restart thread
        if (len(self._scheduled_tasks) and self._active) or len(self._active_tasks):
            self._main_proc_timer = threading.Timer(1, self._main_proc)
            self._main_proc_timer.start()
        else:
            #print('main: lock run')
            self._lock_run.acquire()
            self._running = False
            #print('main: unlock run')
            self._lock_run.release()

    def _run_task(self, task):
        """
        activate task job
        """
        task.thread = threading.Thread(target=task.routine)
        task.thread.start()
        
    def _activate_tasks(self):
        """
        activate some tasks
        """
        #print('_act: lock shed')
        self._lock_sched.acquire()
        try:
            activating_task_count = min(
                    len(self._scheduled_tasks),
                    self._max_active_tasks - len(self._active_tasks)
            )
            tasks_to_activate = self._scheduled_tasks[:activating_task_count]
            self._scheduled_tasks = self._scheduled_tasks[activating_task_count:]
        finally:
            #print('_act: unlock shed')
            self._lock_sched.release()
        #print('_act: lock act')
        self._lock_act.acquire()
        try:
            map(self._run_task, tasks_to_activate)
            self._active_tasks += tasks_to_activate
        finally:
            #print('_act: unlock act')
            self._lock_act.release()

    def _gather_completed_tasks(self):
        """
        Look for completed tasks and
        move them from _active_tasks to _completed_tasks 
        """
        #print('gath: lock act')
        self._lock_act.acquire()
        try:
            completed = []
            for task in self._active_tasks:
                if task.complete:
                    completed.append(task.result)
                    task.gathered = True
            self._active_tasks = filter(lambda t: not t.gathered, self._active_tasks)
        finally:
            #print('gath: unlock act')
            self._lock_act.release()
        #print('gath: lock compl')
        self._lock_compl.acquire()
        try:
            self._completed_tasks += completed
        finally:
            #print('gath: unlock compl')
            self._lock_compl.release()

    def activate(self):
        """
        Start _main_proc()
        """
        #print('act: lock run')
        self._lock_run.acquire()
        try:
            if not self._running:
                self._main_proc_timer = threading.Timer(1, self._main_proc)
                self._main_proc_timer.start()
                self._running = True
        finally:
            #print('act: unlock run')
            self._lock_run.release()

    def add_task(self, task):
        """
        Enqueue new task
        """
        #print('add: lock shed')
        ret_value = True
        self._lock_sched.acquire()
        try:
            self._scheduled_tasks.append(task)
            if len(self._scheduled_tasks) > self._max_scheduled_tasks:
                ret_value = False
        finally:
            #print('add: unlock shed')
            self._lock_sched.release()
        self.activate()
        return ret_value

    def get_loaded_page(self):
        """
        Get the first loaded page
        Returns namedtuple('url, code, info, data, user_data')
        """
        ret_value = None
        #print('get: lock compl')
        self._lock_compl.acquire()
        try:
            if self._completed_tasks:
                ret_value = self._completed_tasks.pop(0)
        finally:
            #print('get: unlock compl')
            self._lock_compl.release()
        return ret_value

    def get_loaded_page_filtered(self, filter_match):
        """
        Returns namedtuple('url, code, info, data, user_data')
        """
        ret_value = None
        self._lock_compl.acquire()
        try:
            for task in self._completed_tasks:
                if filter_match(task):
                    ret_value = task
                    break
            if ret_value:
                self._completed_tasks.remove(ret_value)
        finally:
            #print('get: unlock compl')
            self._lock_compl.release()
        return ret_value

    def purge_tasks(self, filter_not_match, from_queues = 3):
        """
        Cancels all active/scheduled tasks and deletes all completed tasks
        """
        locks = 0
        while locks < 4:
            if self._lock_sched.acquire(False):
                locks += 1
            if self._lock_compl.acquire(False):
                locks += 1
            if self._lock_act.acquire(False):
                locks += 1
            if self._lock_run.acquire(False):
                locks += 1
            if locks < 4:
                sleep(0.01)
        if from_queues > 0:
            self._scheduled_tasks = filter(filter_not_match, self._scheduled_tasks)
        if from_queues > 1:
            self._active_tasks = filter(filter_not_match, self._active_tasks)
        if from_queues > 2:
            self._completed_tasks = filter(filter_not_match, self._completed_tasks)

        self._lock_sched.release()
        self._lock_compl.release()
        self._lock_act.release()
        self._lock_run.release()

    def have_slots(self):
        return len(self._scheduled_tasks) < self._max_scheduled_tasks