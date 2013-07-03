#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Alex Turkin <snowwlex@gmail.com>"



import sys, os.path, glob
from Trigrams import Trigrams
from lid import clean_punctuation_from_text

sys.path.insert(1,'../')
import chardet

if __name__ == "__main__":
    myTrigrams = Trigrams()
    if len(sys.argv) > 1:
        for x in sys.argv[1:]:
            for y in glob.glob(os.path.normcase(x)):
                try:
                    f = open(y)
                    string = f.read()
                    encoding = chardet.detect(string)['encoding']
                    unistring = unicode(string, encoding)#.decode(encoding)
                    cleaned =  clean_punctuation_from_text(unistring)
                    myTrigrams.add_trigrams_from_text(cleaned)
                except IOError:
                    pass

        myTrigrams.eliminate_frequences(2)
        myTrigrams.calculate_probabilities()
        pairs = zip(myTrigrams.trigrams.keys(), myTrigrams.trigrams.values())
        pairs.sort()
        pairs.reverse()
        for i in pairs:
            string = "%s   %s"  % (i[0], i[1])
            print string.encode('utf-8')
    else:
        print "Usage:"
        print "python lidtrainer.py [document1] ..."
        print "outputs stats by trigrams"


