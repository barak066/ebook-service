#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from analyser.adds import logger
from . import BaseTaskManager
from analyser.settings import TM_DELAY_EACH, TM_DELAY_TIME

"""
in this package:
implementations of TaskManager
"""

class SimpleTaskManager(BaseTaskManager):
    "implements idea about executing tasking, if necessary download pages for them, and saves info about bad task"
    #TODO process case: looping through the site
    def __init__(self, *args):
        super(SimpleTaskManager,self).__init__(*args)

    def run(self):
        try:
            while self.loop_condition():
                self.tasks_executing_loop()
        except KeyboardInterrupt:
            pass
        except:
            logger.write_fail('global unknown error')
            print logger.generate_text('SimpleTaskManager: global error')
        self.storage.close()

    def loop_condition(self):
        return self.storage.has_task()

    def tasks_executing_loop(self):
        task = self.storage.get_task()
        if task.need_html:
            page = self.download_task(task)
            if not page:
                return
        else:
            page = ()
        self.print_executing(task)
        self.execute_task(task, page)

    def download_task(self, task):
        print '    downloading: %s' % task.link
        try:
            page = (self.dm.download(task.link) , )
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            self.got_bad_task(task)
            return None
        else:
            return page


    def execute_task(self,task, params):
        try:
            task.execute(*params)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            self.got_bad_task(task)
        else:
            self.storage.mark_executed()
            self.storage.accept_new_tasks( task.get_tasks() )

    def got_bad_task(self,task):
        print 'BAD TASK!'
        task.what_bad = logger.generate_text('bad task', task=task)
        self.storage.mark_task_bad()
        logger.write_fail("bad task!", task=task)

    def print_executing(self,task):
        print '    executing: %s%s' % (task.get_parser_name(), task.get_name() ) #, '<%d left>' % self.holder.count_left_tasks()
        pass


class DelayingSimpleTaskManager(SimpleTaskManager):
    "make delay for reducing loading of server"
    def __init__(self, *args):
        super(DelayingSimpleTaskManager, self).__init__(*args)
        self.time = time.time()

    def tasks_executing_loop(self):
        if (time.time() - self.time) > TM_DELAY_EACH:
            self._delaying(TM_DELAY_TIME)
        super(DelayingSimpleTaskManager,self).tasks_executing_loop()

    def _delaying(self,sec):
        print 'waiting %d seconds...' % sec
        time.sleep(sec)
        self.time = time.time()

