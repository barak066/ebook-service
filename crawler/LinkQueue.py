# -*- coding: UTF-8 -*-
__author__ = 'pxanych'

from Queue import Full, Empty
from crawler.linkFunctions import get_netlock

class LinkQueue(object):

    def __init__(self, maxlen = 2147483647):
        self.maxlen = maxlen
        self._queue = []

    def put(self, item, push = False):
        if type(item) != tuple:
            raise AttributeError('<item> must have tuple type')
        if len(self._queue) >= self.maxlen and not push:
            raise Full
        k, v = item
        index = 0
        for list_k, list_v in self._queue:
            if k > list_k:
                index += 1
            else:
                break
        self._queue.insert(index, item)
        if len(self._queue) > self.maxlen:
            self._queue = self._queue[:self.maxlen]

    def get(self):
        if self._queue:
            return self._queue.pop()[1]
        raise Empty

    def drop(self, count):
        q_length = len(self._queue)
        self._queue = self._queue[ : q_length - max(q_length, count)]

    def filter(self, filter_function):
        filtered_out = []
        staying = []
        for item in self._queue:
            if filter_function(item):
                staying.append(item)
            else:
                filtered_out.append(item)
        self._queue = staying
        return filtered_out

    def is_empty(self):
        return len(self._queue) == 0
    


  