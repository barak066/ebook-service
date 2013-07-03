# -*- coding: UTF-8 -*-
__author__ = 'Павел'

from threading import Lock, Thread, Timer
from collections import namedtuple
from time import sleep

class Worker(object):

    def __init__(self):
        self._scheduled_tasks = []
        self._completed_tasks = []
        self._active_tasks = []
        locks_class = namedtuple('locks_class', 'act, compl, sched, run' )
        self._locks = locks_class(Lock(), Lock(), Lock(), Lock())
        self._running = False
        self._main_proc_timer = None
        self._max_active_tasks = 16
        self._max_scheduled_tasks = 512
        self._active = True

    def _enter_sleep_mode(self):
        """
        Enter sleep mode:
            all active tasks are completed
        """
        self._active = False
        while self._running:
            sleep(1)
        return True

    def _wake_up(self):
        """
        Leave sleep mode
        """
        self._active = True
        self.activate()

    def _main_proc(self):
        """
        while have tasks: do some work
        """
        self._gather_completed_tasks()
        if self._active:
            self._activate_tasks()
        #if have more job to do - wait for 1 second and restart thread
        if (len(self._scheduled_tasks) and self._active) or len(self._active_tasks):
            self._main_proc_timer = Timer(1, self._main_proc)
            self._main_proc_timer.start()
        else:
            #print('main: lock run')
            self._locks.run.acquire()
            self._running = False
            #print('main: unlock run')
            self._locks.run.release()

    def purge_tasks(self, filter_not_match):
        """
        Cancels all active/scheduled tasks and deletes all completed tasks,
        for which <filter_not_match> returns False.
        """
        locks = 0
        while locks < 4:
            if self._locks.sched.acquire(False):
                locks += 1
            if self._locks.compl.acquire(False):
                locks += 1
            if self._locks.act.acquire(False):
                locks += 1
            if self._locks.run.acquire(False):
                locks += 1
            if locks < 4:
                sleep(0.01)
        self._active_tasks = filter(filter_not_match, self._active_tasks)
        self._completed_tasks = filter(filter_not_match, self._completed_tasks)
        self._scheduled_tasks = filter(filter_not_match, self._scheduled_tasks)
        for lock in self._locks:
            lock.release()

    def _run_task(self, task):
        """
        activate task job
        """
        task.thread = Thread(target=task.routine, args = (task, task.args))
        task.thread.start()

    def _activate_tasks(self):
        """
        activate some tasks
        """
        #print('_act: lock shed')
        self._locks.sched.acquire()
        try:
            activating_task_count = min(
                    len(self._scheduled_tasks),
                    self._max_active_tasks - len(self._active_tasks)
            )
            tasks_to_activate = self._scheduled_tasks[:activating_task_count]
            self._scheduled_tasks = self._scheduled_tasks[activating_task_count:]
        finally:
            #print('_act: unlock shed')
            self._locks.sched.release()
        #print('_act: lock act')
        self._locks.act.acquire()
        try:
            map(self._run_task, tasks_to_activate)
            self._active_tasks += tasks_to_activate
        finally:
            #print('_act: unlock act')
            self._locks.act.release()

    def _gather_completed_tasks(self):
        """
        Look for completed tasks and
        move them from _active_tasks to _completed_tasks
        """
        #print('gath: lock act')
        self._locks.act.acquire()
        try:
            completed = []
            for task in self._active_tasks:
                if task.complete:
                    completed.append(task)
                    task.gathered = True
            self._active_tasks = filter(lambda t: not t.gathered, self._active_tasks)
        finally:
            #print('gath: unlock act')
            self._locks.act.release()
        #print('gath: lock compl')
        self._locks.compl.acquire()
        try:
            self._completed_tasks += completed
        finally:
            #print('gath: unlock compl')
            self._locks.compl.release()

    def activate(self):
        """
        Start _main_proc()
        """
        #print('act: lock run')
        self._locks.run.acquire()
        try:
            if not self._running:
                self._main_proc_timer = Timer(1, self._main_proc)
                self._main_proc_timer.start()
                self._running = True
        finally:
            #print('act: unlock run')
            self._locks.run.release()

    def add_task(self, task):
        """
        Enqueue new task
        """
        #print('add: lock shed')
        self._locks.sched.acquire()
        try:
            self._scheduled_tasks.append(task)
        finally:
            #print('add: unlock shed')
            self._locks.sched.release()
        self.activate()

    def get_completed_task_deprecated(self):
        """
        get the first completed task
        """
        ret_value = None
        #print('get: lock compl')
        self._locks.compl.acquire()
        try:
            ret_value = self._completed_tasks.pop(0)
        except IndexError:
            ret_value = None
        finally:
            #print('get: unlock compl')
            self._locks.compl.release()
        return ret_value

    def get_completed_task(self, filter_match = (lambda x: True)):
        ret_value = None
        self._locks.compl.acquire()
        try:
            for task in self._completed_tasks:
                if filter_match(task):
                    ret_value = task
                    break
            if ret_value:
                self._completed_tasks.remove(ret_value)
        finally:
            #print('get: unlock compl')
            self._locks.compl.release()
        return ret_value

    def ready_to_shutdown(self):
        self._locks.sched.acquire()
        l_s = len(self._scheduled_tasks)
        self._locks.sched.release()
        self._locks.act.acquire()
        l_a = len(self._active_tasks)
        self._locks.act.release()
        self._locks.compl.acquire()
        l_c = len(self._completed_tasks)
        self._locks.compl.release()
        return l_s + l_a + l_c == 0


