#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = 'snowwlex'

import re
import sys
from string import *



class Trigrams:
    """
    stores trigrams
    """
    def __init__(self):
        self.clean_trigrams()

    def clean_trigrams(self):
        self.trigrams = {}   # tri-grams are stored in a dictionary
        self.num = 0        # number of tri-grams
        self._characters = 0 # number of characters

    def create_trigrams(self,text):
        self.clean_trigrams()
        self.add_trigrams_from_text(text)
    
    def add_trigrams_from_text(self, text):
        """Creates trigrams from characters."""
        text = re.sub(r"\n", r" ", text)
        text = re.sub(r"\s+", r" ", text)
        self._characters = self._characters + len(text)
        for i in range(len(text) - 2):
            trigram = text[i:i+3]
            trigram = trigram.lower()
            if self.trigrams.has_key(trigram):
                self.trigrams[trigram] += 1
            else:
                self.trigrams[trigram] = 1
            self.num += 1
            
    def add_trigram(self, trigram, probability):
        self.trigrams[trigram] = probability

    def calculate_probabilities(self):
        """Calculate the probabilities for each trigram."""
        for x in self.trigrams.keys():
            self.trigrams[x] = float(self.trigrams[x]) / float(self.num)

    def eliminate_frequences(self, num):
        """Eliminates all bigrams with a frequency <= num"""
        for x in self.trigrams.keys():
            if self.trigrams[x] <= num:
                value = self.trigrams[x]
                del self.trigrams[x]
                self.num -= value

    def get_contains(self, regexp):
        l = []
        for k,v in self.trigrams.items():
            if re.match(regexp, k):
                l.append( (k,v) )
        return l




