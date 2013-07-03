#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import time

from crawler.Worker import Worker
from crawler.WorkerTask import WorkerTask

from analyser.adds import logger


import analyser.settings

TM_WAITING_TIME  = getattr(analyser.settings, 'TM_WAITING_TIME')
DOWNLOAD_COUNT = getattr(analyser.settings,'TM_DOWNLOAD_COUNT')

class DownloadTask:
    #TODO this class is temporal decision for routine functions
    "WorkerTask-like object"
    def __init__(self, args, user_data = None):
        self.args = args
        self.user_data = user_data
        self.result = []

class DownloadManager:

    def __init__(self, mode, other_routine=None):
        self.tasks = []
        self.tasks_completed = []
        self.mode = mode
        if mode==0:
            self._worker = Worker()
        self._tasks_downloading = []
        self._data = {}
        self._sleeping_time = None
        self.waiting = TM_WAITING_TIME
        self._right_time = True
        self._routine = other_routine if other_routine else routine
        pass

    def run(self):
        if self.mode==0:
            self._set_to_upload()
            self._asking_worker()
        else:
            self._usual_downloading()

    def get_completed_tasks(self):
        completed = self.tasks_completed
        self.tasks_completed = []
        return completed

    def _usual_downloading(self):
        if self.tasks:
            self.tasks.sort(key=lambda t: t.weight)
            task = self.tasks.pop(0)
            print 'adding download task', task
            dtask = DownloadTask([], task)
            self._routine(dtask,[])
            result = dtask.result
            self._data[task.link] = (result['data'], result['page'])
            self.tasks_completed.append(task)


    def get_html(self,link):
        if link in self._data:
            html = self._data[link]
            del self._data[link]
            return html
        return None

    def is_finished(self):
        result = not (self._sleeping_time or self._tasks_downloading or self.tasks)
        return result

    def _set_to_upload(self):
        if not self._is_sleep():
            need_download = DOWNLOAD_COUNT - len(self._tasks_downloading)
            if need_download < 1:
                return
            self.tasks.sort(key=lambda t: t.weight)
            for task in self.tasks[:need_download]:
                print 'adding download task', task
                self._worker.add_task( WorkerTask([], self._routine, task) )
                self.tasks.remove(task)
                self._tasks_downloading.append(task)

    def _get_completed_tasks(self):
        while True:
            worker_task = self._worker.get_completed_task()
            if not worker_task:
                break
            yield worker_task.user_data, worker_task.result

    def _asking_worker(self):
        if not self._is_sleep():
            for task, result in self._get_completed_tasks():
                if result['page'].getcode() == 503:
                    self._set_sleep_mode()
                    return
                self._data[task.link] = (result['data'], result['page'])
                self._tasks_downloading.remove(task)
                self.tasks_completed.append(task)
                self._right_time = True

    def _set_sleep_mode(self):
        self._rise_up_waiting()
        print 'set sleeping mode at', self.waiting, 'seconds...'
        self._worker.purge_tasks(lambda task: True )
        self.tasks.extend(self._tasks_downloading)
        self._tasks_downloading = []
        self._sleeping_time = time.time()
        self._right_time = False

    def _rise_up_waiting(self):
        if not self._right_time:
            self.waiting *= 1.5


    def _is_sleep(self):
        if not self._sleeping_time:
            return False
        past_time = time.time()-self._sleeping_time
        if past_time >= self.waiting:
            self._sleeping_time = None
            return False
        return True



def routine(self, args):
    "Page loading routine"
    page = urllib.urlopen(self.user_data.link)
    if 'get_bytes' in self.user_data.__dict__:
        get_bytes = self.user_data.get_bytes
        print 'downloading ', get_bytes, 'bytes from link', self.user_data.link
        data = page.read( get_bytes )
    else:
        data = page.read()
    page.close()
    self.result = { 'task'    : self.user_data,
                    'headers' : page.headers,
                    'data'    : data,
                    'page'    : page,
                  }
    self.complete = True



