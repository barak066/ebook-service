#!/usr/bin/env python
# -*- coding: utf-8 -*-

import runners
import os

path_to_project = runners.get_project_dir(__file__)
ADD_TO_PATH = ('server', 'lib')


DEBUG_MODE = True

#FOLDERS
data = 'data/'
analyser = 'analyser/'
LOGS_FOLDER = os.path.join(path_to_project,analyser,data,'logs')
STATE_FOLDER = os.path.join(path_to_project,analyser,data,'states')
CACHE_FOLDER =  os.path.join(path_to_project,analyser,data,'cache')
LID_STAT_FOLDER = os.path.join(path_to_project,'lib/lid/stat/')

#FILES POSTFIXES
STATE_FILE_POSTFIX = '.state'
LOG_FILE_POSTFIX = '.txt'


#TASK MANAGER SETTINGS
TM_WAITING_TIME = 20*60 #waits (in seconds)
TM_LONGTERM_NUMBER = 10
TM_DOWNLOAD_COUNT = 10
#SETTINGS SERVER LOADING PROBLEM
TM_DELAY_EACH = 30 #every n seconds
TM_DELAY_TIME = 10 #delay at m seconds


#PARSERS

#FLIBUSTA.NET
#personal information, should be setted in local_settings
FLIBUSTA_USER = 'xxx'
FLIBUSTA_PASS = 'xxx'

#LIB.RU
LIBRU_DEFINE_LANG_BY_BYTES = 2048*2 #how many first bytes from parser LibRu will use for defining language
LIBRU_IGNORE_DIRS = ['COPYRIGHT', 'COMPULIB','win','koi','lat','Forum','Mirrors','WEBMASTER']
LIBRU_IGNORE_BOOKS = ['copyright.txt', 'TXT/listing.txt', 'TXT/help_search.txt', 'TXT/incoming.txt',
                      'KSP/thanks.txt']



#os.environ['http_proxy'] = 'http://192.168.0.2:3128/'


try:
    from local_settings import *
except Exception:
    pass