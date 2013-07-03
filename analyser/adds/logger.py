"""
this file contains all debug helper methods that i use  for debugging
"""
import sys
import os
from traceback import print_exception, format_exception
from datetime import datetime

from analyser.settings import DEBUG_MODE, LOGS_FOLDER, LOG_FILE_POSTFIX
from server.django.utils.encoding import force_unicode

_debug_env = 'analyser_debug_filename' #used for storing debug filename in OS' environment

def set_file(filename):
    os.environ[_debug_env] = filename

def _get_debug_filename():
    return os.environ.pop(_debug_env, 'std_debug')

def write(title, **kwargs):
    "writes debug info to setted file"
    to_file( _get_debug_filename(), title, **kwargs )
    pass

def write_fail(title, **kwargs):
    "write about fail"
    to_file( 'fail' , title, **kwargs )
    pass

def write_success(title, **kwargs):
    "write about sucess"
    to_file( 'success' , title, **kwargs )
    pass

def to_file(filename, title, **kwargs):
    """print something to debug_file"""
    if not DEBUG_MODE:
        return
    if not os.path.exists(LOGS_FOLDER):
        os.makedirs(LOGS_FOLDER)
    filename = os.path.join(LOGS_FOLDER, filename + LOG_FILE_POSTFIX)
    debug_file = open(filename, 'a')
    text = generate_text(title, **kwargs)
    #TODO work out with unicode in python and encoding problems
    #print type(text)
    debug_file.write( text.encode('utf8')   )
    debug_file.write('-'*80+'\n')
    debug_file.close()

def generate_list(title, **kwargs):
    l = []
    when = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    l.append( "%s, %s" % (when, title) )
    for key, value in kwargs.items():
        if type(value) == unicode:
            s = key +  ' : ' + value.encode('utf8')
        else:
            s = key + ' : ' + str(value)
        l.append(s)
    err_type, value, traceback = sys.exc_info()
    if traceback:
        l.extend( format_exception(err_type, value, traceback, None) )
    return l


def generate_text(title, **kwargs):
    list = [ force_unicode(el) for el in generate_list(title, **kwargs)]
    return u"\n".join( list  )
