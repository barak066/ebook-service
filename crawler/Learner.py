# -*- coding: UTF-8 -*-
__author__ = 'pxanych'

import globalcrawersettings

class Learner(object):

    def __init__(self):
        self.words_good = {}
        self.words_all = {}

    def load_words(self, filename):
        f = file(filename, 'r')
        pairs = f.read().split('\r\n')[:-1]
        d = {}
        for pair in pairs:
            word, percent = pair.split(' : ')
            word = word.decode('utf8')
            percent = float(percent)
            d[word] = percent
        return d

    def save_words(self, filename, word_dict):

        f = file(filename, 'r')


