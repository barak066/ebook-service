#!/usr/bin/env python
# -*- coding: utf-8 -*-


""" made for test processing authors name """
import os

authors_dir = 'doc/authors/'

def gen_filename(name):
    return authors_dir + name + '.txt'

class AuthorList:
    "wrapper over set"
    def __init__(self, name):
        self.set = set()
        self.name = name
        self._load_set()
        self.add_queue = []
        self.remove_queue = []
        self.in_iter = False

    def __iter__(self):
        self.process_queue()
        self.in_iter = True
        for name in self.set:
            yield name
        self.in_iter = False
        self.process_queue()
        
    def _load_set(self):
        if os.path.exists(gen_filename(self.name)):
            for line in open(gen_filename(self.name) , 'r').readlines():
                line = unicode(line,'utf-8')
                self.set.add(line)
    def add(self,name):
        self.add_queue.append(name)
        if not self.in_iter:
            self.process_queue()

    def remove(self,name):
       self.remove_queue.append(name)
       if not self.in_iter:
            self.process_queue()
           
    def process_queue(self):
        for e in self.add_queue:
            self.set.add(e)
        for e in self.remove_queue:
            self.set.remove(e)
        self.add_queue, self.remove_queue = ([], [])
        
    def save(self):
        self.process_queue()
        f = open(gen_filename(self.name), 'w')
        for name in self.set:
            f.write(name.encode('utf-8'))
        f.close()