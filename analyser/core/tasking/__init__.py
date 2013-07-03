#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
in this package: base classes for tasking

BaseTask is base object for all tasks

BaseTaskStorage is part that stores  some tasks (getting it from DB, or file, or etc)
and can use some policy for task priority executing
used by TaskManager
"""

import re
import urllib

class BaseTask(object):
    #TODO add version descriptor for serialization
    def __init__(self):
        self.tasks = []
        self.longterm = False
        self.need_html = False
        self.weight = 0

    def __repr__(self):
        return '<%s>' % self.get_name()
    def execute(self):
        print 'empty task'
        return True
    def get_tasks(self):
        return self.tasks
    def get_name(self):
        name = str(type(self))
        pattern = "\.([A-Za-z_-]+)'>$"
        return re.search(pattern,name).groups()[0]
    def get_parser_name(self):
        name = str(type(self))
        pattern = "\.([A-Za-z_-]+\.)tasks.+$"
        m =  re.search(pattern,name)
        return m.groups()[0] if m else ''

class NeedHTMLTask(BaseTask):
    def __init__(self,link):
        super(NeedHTMLTask,self).__init__()
        self.need_html = True
        self.link = link
    def __repr__(self):
        return '<%s: %s>' % (self.get_name(), self.link)


class NoTask(Exception):
    "exception that raises when there's not tasks in storage"
    pass

class BaseTaskStorage:
    "stores tasks, allow get and give them"
    def __init__(self):
        pass

    def re_run(self):
        "re_run task holding (start from initial tasks again)"
        pass

    def has_task(self):
        return False

    def mark_executed(self):
        "marks task as executed"
        pass

    def mark_task_bad(self):
        "marks task as bad"
        pass

    def get_task(self):
        "returns task or throws NoTask if task not existed"
        raise NoTask

    def accept_new_tasks(self, tasks):
        "accept tasks"
        pass

    def count_left_tasks(self):
        return 0

    def close(self):
        "says to Holder that it won't be use anymore"
        pass


class BaseTaskManager(object):
    "base class for TaskManager, used like interface to any TaskManager"
    def __init__(self, task_storage, download_manager):
        self.storage = task_storage
        self.dm = download_manager
    def run(self):
        pass


class BaseDownloadManager(object):
    "base class for DownloadManager, used like interface to any DownloadManager"
    def __init__(self):
        pass

    def download(self,link):
        return (None, None) #data, page

    def read_data(self,page):
        return page.read()

    def get_page(self, link):
        return urllib.urlopen(link)