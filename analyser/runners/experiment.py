#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from posix import getcwd
import sys
import re
import time

from server.book.models import Author, Book
from analyser import runners
from analyser.updaters.authors_processing import AuthorList
from lib.lid.lid import Lid
from analyser.adds.preprocessing import preprocess_author, preprocess_authors
from lib.lid.Trigrams import Trigrams

def main(argv, **kwargs):
    prefix = 'exp_'
    command, _ = runners.get_command(kwargs['dir'], argv, prefix, 'experiment', lambda doc: eval(doc))
    if command:
        c = eval(prefix+command)
        c()



def get_trigrams():
    from string import *
    import analyser.settings
    STAT_DIR = getattr(analyser.settings, 'LID_STAT_FOLDER', getcwd())
    x = 'ru.dat'
    modelfile = file(os.path.join(STAT_DIR,x))
    model = Trigrams()
    for line in modelfile:
        tokens = line.split()
        if len(tokens) == 2:
            trigram = lower( unicode( tokens[0],'utf-8') )
            probability = float(tokens[1])
            model.add_trigram(trigram,probability)
    return model

def exp_generate():
    "generating text over trigrams"

    model = get_trigrams()
    while True:
        word = get_word(model)
        print word.encode('utf-8')

def get_word(model):
    import random
    main = model.trigrams.keys()[ random.randint(0, len(model.trigrams))]
    #print main,
    while True:
        if len(main) > 3:
            if random.randint(1,4) == 3:
                break
        last_2 = main[-2:]
        contains = model.get_contains(last_2+".")
        if not contains:
            break
        contains.sort(key=lambda t: t[1],reverse=True)
        add = contains[0][0][-1:]
        main += add
        #raw_input()
    return main

def get_authors(text):
    points =  text.split('. ')
    return [ points[0] ]
#    authors = []
#    for p, _ in enumerate(points):
#        authors.append(". ".join(points[0:p]))
#        #print points[0:p].encode('utf-8')
#    return authors

def is_author(text):
    filters = [ u"^[А-Яа-я]{1,2}\.\s?[А-Яа-я]{1,2}\.\s?[A-Яа-я-]+" ,
                u"^[А-Я]\.\s*[А-Я][A-Яа-я-]+$" ,
                u"^[А-Я][а-я]\.\s*[А-Я][A-Яа-я-]+$" ,
                u"^[А-Яа-я]+\s+[А-Я][А-Яа-я]+$",
                u"^[А-Я][а-я]+\s+[А-Я][а-я]+\s+[А-Я][а-я]+$",
              ]
    exclusions = [ u'Речь' ]
    if any ( re.search('%s' % exclusion, text) for exclusion in exclusions) :
        return -1, False
    for n, filter in enumerate(filters):
        if re.match( filter, text):
            return n, True
    return -1,False

def exp_extract_authors():
    "extracting authors from libru"
    f = open('data/authors2.txt')
    for line in f.readlines():
        line = unicode(line,'utf-8')
        authors = get_authors(line)
        authors = preprocess_authors( authors )
        for author in authors:
            print is_author(author), "'%s'" % author.encode('utf-8') #print author.encode('utf-8')
    pass

def not_exp_get_authors_lists():
    authors = Author.objects.all()
    counts = [author.book_set.count() for author in authors]
    ac = zip( (author.name for author in authors), counts)
    ac_new =  sorted(ac, key=lambda a: a[1], reverse=True )
    for a in ac_new:
        name,count = a
        print name.encode('utf-8')

def not_exp_proc_authors():
    source = AuthorList('heap')
    final = AuthorList('initials')
    for name in source:
        new_name = name.replace('.', ' ')
        words = new_name.split()
        if any( map( lambda name: len(name) == 1, words ) ):
            final.add(new_name)
            source.remove(name)
    source.save()
    final.save()


def exp_exp():
    myLid = Lid()
    path = '/home/snowwlex/ws/d_books/'
    lang = 'ru'
    mode = 'new'
    fullpath = path + "/".join([lang,mode]) + "/"
    #for root, dirs, files in os.walk(path):
    files = os.listdir( fullpath )
    languages = {}
    problems = []

    start_time = time.time()
    print "n;file;language;confidence;ru;en;de;fr"
    for n, file in enumerate(files):
        try:
            f = open(fullpath + file)
            text = read_text(f)
            language, answer = myLid.checkText(text )
            if languages.has_key(language):
                languages[language] += 1
            else:
                languages[language] = 1
            print "%d;%s;%s;%f;%d;%d;%d;%d" % (n, file, language, answer['confidence'], \
                answer['stat']['ru'], answer['stat']['en'], answer['stat']['de'],answer['stat']['fr'])
            f.close()
        except UnicodeDecodeError:
            problems.append(file)
            
    print languages
    
    print '\nPROBLEMS:' 
    for problem in problems:
        print problem

    end_time = time.time()
    print 'seconds for this experiment: ', (end_time - start_time)

def read_text(file):
    text = "\n".join(file.readlines())
    text = unicode(text, 'utf-8')
    return text

    
def not_exp_1():
    from parsers.LibRu import LibRu
    parser = LibRu()
    import pickle
    f = file('test.txt','w')
    pickle.dump(parser,f)
    f.close()

def exp_show_q_books():
    import time
    from server.book.models import Book
    seconds = 0
    init_books = Book.objects.all().count()
    try:
        while True:
            time.sleep(5)
            seconds += 1
            qb = Book.objects.all().count()
            speed = float((qb - init_books)) / (seconds*5)
            print qb, "%f books/sec" % speed
            
    except KeyboardInterrupt:
        print 'all'
#    except:
#        pass  


