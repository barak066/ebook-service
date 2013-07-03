#!/usr/bin/env python
# -*- coding: utf-8 -*-

from analyser.adds.State import State
from analyser.adds import logger
from server.django.db.models import Q
from server.analyser_app.models import Task as DBTask
from . import NoTask, BaseTaskStorage


"""
in this package:
implementations of TaskStorage
"""


class TaskStorageDB(BaseTaskStorage):
    "stores tasks in DataBase, getting them in priority order (by weight"
    def __init__(self, name, initial_tasks, query=Q(good=True) ):
        self.query = query
        self.curtask = None
        self.name = name
        self.initial_tasks = initial_tasks
        self._initiate()

    def _initiate(self):
        if not self.has_task():
            for task in self.initial_tasks:
                dbtask = self._create_db_task(task)
                dbtask.save()

    def re_run(self):
        DBTask.objects.filter(self.query).delete()
        self._initiate()

    def has_task(self):
        count = DBTask.objects.filter(self.query).count()
        return count > 0

    def mark_executed(self):
        if self.curtask:
            if self.curtask.good == True:
                self.curtask.delete()
            self.curtask = None
        else:
           logger.write_fail("Task DB Storage,strange behavior", task=str(self.curtask))

    def mark_task_bad(self):
        if self.curtask:
            self.curtask.good = False
            self.curtask.reason = self.curtask.serialized_task.what_bad
            self.curtask.save()
        else:
            logger.write_fail("Task DB Storage,strange behavior", id=self.curtask.id)


    def get_task(self):
        "returns task or throws NoTask if task not existed"
        tasks = DBTask.objects.filter(self.query).order_by('weight')[:1]
        if not tasks:
            raise NoTask
        task = tasks[0]
        self.curtask = task
        return task.serialized_task

    def accept_new_tasks(self, tasks):
        "accept tasks"
        for task in tasks:
            dbtask = self._create_db_task(task)
            dbtask.save()

    def count_left_tasks(self):
        count = DBTask.objects.filter(self.query).count()
        return count

    def close(self):
        "says to Holder that it won't be use anymore"
        pass

    def _create_db_task(self,task):
        #TODO may be there should be unique checking? (unique with link,task name (and may be parser_name)
        # if unique, should not be setted agagin
        # it will solve problem with looping by links
        dbtask = DBTask()
        dbtask.serialized_task = task
        dbtask.parser_name =  self.name
        dbtask.name = task.get_name()
        dbtask.weight = task.weight
        if 'link' in task.__dict__:
            dbtask.link = task.link
        return dbtask






class StateTaskStorage(State):
    def __init__(self,type,filename):
        State.__init__(self,type,filename)
        self.tasks = []
        self.bad_tasks = []
        self.initialized = False


class TaskStorageStated(BaseTaskStorage):
    "holds tasks, allow get and give them. implements by using States (saves data into file)"
    def __init__(self, state_name, state_type, initial_tasks):
        self.state = StateTaskStorage(state_type, state_name)
        self.name = state_name
        self.type = state_type
        self.curtask = None
        self.initial_tasks = initial_tasks
        self._load_state()
        self._initial()

    def re_run(self):
        self.state.initialized = False
        self._initial()

    def has_task(self):
        result = True if self.state.tasks else False
        return result

    def mark_executed(self):
        if self.curtask:
            self.state.tasks.remove(self.curtask)
            self.curtask = None
        else:
            logger.write("Task Stated Storage,strange behavior", task=self.curtask)

    def mark_task_bad(self):
        if self.curtask:
            self.state.bad_tasks.append(self.curtask)
            self.mark_executed()
            self.curtask = None

    def get_task(self):
        if not self.state.tasks:
            raise NoTask
        self.curtask = self.state.tasks[0]
        return self.curtask

    def accept_new_tasks(self, tasks):
        self.state.tasks.extend(tasks)

    def count_left_tasks(self):
        return len( self.state.tasks )

    def close(self):
        self._save_state()

    def _initial(self):
        if not self.state.initialized:
            self.state.initialized = True
            self.state.tasks = self.initial_tasks
            self._save_state()

    def _load_state(self):
        self.state.load()

    def _save_state(self):
        print 'saving state'
        self.state.save()




class TaskStorageStatedPriority(TaskStorageStated):
    "stores tasks, and get him in priority order (by weight) "
    def accept_new_tasks(self, tasks):
        self.state.tasks.extend(tasks)
        self.state.tasks.sort( self.sorting )

    @staticmethod
    def sorting(task1,task2):
        if task1.weight < task2.weight:
            result =  -1
        if task1.weight == task2.weight:
            result =  0
        if task1.weight > task2.weight:
            result =  1
        if task1.longterm and task2.longterm:
            return result
        if task1.longterm:
            return -1
        elif task2.longterm:
            return 1
        return result