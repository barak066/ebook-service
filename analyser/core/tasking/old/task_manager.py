#!/usr/bin/env python
# -*- coding: utf-8 -*-

from analyser.adds import logger
from analyser.core.tasking.DownloadManager import DownloadManager

import time



class TaskManager:

    def __init__(self, holder, other_routine=None):
        self.holder = holder
        self.dm = DownloadManager(1, other_routine)
        self.time = time.time()
        self.tasks = []

    def run(self):
        try:
            self.tasks_executing_loop()
        except KeyboardInterrupt:
            pass
        except:
            logger.write_fail('global unknown error')
        self.holder.close()

    def tasks_executing_loop(self):
        while self.loop_condition():
            # TODO fix highloading problem another way
            if (time.time() - self.time) > 30:
                self.delaying(10)
            self.pick_task()
            self.tasks_processing()
            self.download_tasks_processing()

    def delaying(self,sec):
        print 'waiting %d seconds...' % sec
        time.sleep(sec)
        self.time = time.time()


    def loop_condition(self):
        return any( [self.tasks, self.holder.has_task(), not self.dm.is_finished() ] )

    def tasks_processing(self):
        if self.tasks:
            task = self.tasks.pop(0)
            self.print_executing(task)
            params = () if not task.need_html else (self.dm.get_html(task.link),)
            try:
                task.execute(*params)
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                self.add_bad_task(task)
            else:
                self.holder.mark_executed()
                self.holder.accept_new_tasks( task.tasks )


    def pick_task(self):
        if not self.tasks and self.holder.has_task():
            task = self.holder.get_task()
            if task.need_html:
                self.dm.tasks.append(task)
            else:
                self.tasks.append(task)

    def download_tasks_processing(self):
        self.dm.run()
        self.tasks += self.dm.get_completed_tasks()

    def add_bad_task(self,task):
        print '\ngot BAD TASK'
        task.what_bad = logger.generate_text('bad task', task=task)
        self.holder.mark_task_bad()
        logger.write_fail("bad task!", task=task)


    def print_executing(self,task):
        print 'executing', task.weight, task, '<%d left>' % self.holder.count_left_tasks()
        pass


