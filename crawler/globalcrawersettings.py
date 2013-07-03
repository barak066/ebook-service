# -*- coding: UTF-8 -*-
__author__ = 'pxanych'

import sys, os, cPickle

sys.path.insert(0, '/home/ebooksearch/webapps/ebook_service/service')
sys.path.insert(0, '/home/pxanych/ebook-service')

#
# TODO: comment next line in production
os.environ['http_proxy'] = 'http://192.168.0.2:3128'
#

from crawler.KeyWords import KeyWords

keyword_global_object = KeyWords
keyword_global_object.load_link_kw()
path_l = os.path.abspath(os.path.curdir).split('/')
os.path.curdir = '/'.join(path_l[:path_l.index('crawler') + 1])

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

def load_settings(s_file):
    if not os.path.exists('res/%s' % s_file):
        return {}
    settings = cPickle.load(file('res/%s' % s_file, 'r'))
    run_id = settings.get('run_id', 0) + 1
    settings['run_id'] = run_id
    backup_dirname = 'res/backup/run_%i' % (run_id - 1)
    if not os.path.exists(backup_dirname):
        os.mkdir(backup_dirname)
    f = file( 'res/backup/run_%(run_id)i/%(file)s' % {'run_id': (run_id - 1), 'file': s_file}, 'w')
    f.write(file('res/%s' % s_file).read())
    f.close()
    return settings

    
def dump_settings(s, s_file):
    cPickle.dump(s, file('res/%s' % s_file, 'w'))

settings = load_settings('settings')

print 'Global settings loaded'