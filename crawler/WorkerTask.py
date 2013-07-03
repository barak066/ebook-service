# -*- coding: UTF-8 -*-
__author__ = 'Павел'

from threading import Lock
import types

class WorkerTask(object):
    """
    This class used to represent page loading task
    """
    def __init__(self, args, routine, user_data = None):
        self._lock_complete = Lock()
        self.__complete = False
        self.gathered = False
        self.args = args
        if callable(routine):
            self.routine = routine
        else:
            raise AttributeError('<routine> argument should be callable function')
        self.user_data = user_data
        self.result = []
        self.thread = None

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

    complete = property(_get_complete, _set_complete)