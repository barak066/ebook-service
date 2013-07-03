#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pickle
import re


import logger


import analyser.settings
STATE_FOLDER = getattr(analyser.settings, 'STATE_FOLDER')
STATE_FILE_POSTFIX = getattr(analyser.settings, 'STATE_FILE_POSTFIX', '.state')


class State(object):
    "saves and stores it's params for saving and loading from file, using pickle;"
    _state_files_prefix = STATE_FOLDER
    _state_files_postfix = STATE_FILE_POSTFIX
    def __init__(self, type, filename):
        path = os.path.join(self._state_files_prefix, type)
        if not os.path.exists(path):
            os.makedirs(path)
        self._filename = os.path.join(path,filename + self._state_files_postfix)
    def load(self):
        if not os.path.exists(self._filename):
            return
        state_file = file( self._filename ,'r')
        state = pickle.load(state_file)
        self._fill_atts_with_state(state)
        state_file.close()
    def save(self):
        #if not os.path.exists(self.m_filename):
        #    raise LookupError("State Error: can't save, no such file '%s'" % self.m_filename)
        state_file = file( self._filename , "w")
        state = self._generate_state_from_atts()
        try:
            pickle.dump(state, state_file)
        except RuntimeError:
            logger.write_fail('stack trace error', state=state)
            raise RuntimeError
        state_file.close()
    def _fill_atts_with_state(self,state):
        for field in self._get_fields():
            if state.has_key(field):
                self.__dict__[field] = state[field]
        pass
    def _generate_state_from_atts(self):
       state = {}
       for field in self._get_fields():
           state[field] = self.__dict__[field] 
       return state
    def _get_fields(self):
        return [ field for field in self.__dict__ if not re.match('^_', field)]
