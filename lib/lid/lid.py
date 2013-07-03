#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "By Alex Turkin <snowwlex@gmail.com>"


import sys, re, os.path, glob
from string import *
from os import listdir, getcwd
from Trigrams import  Trigrams

try:
    import analyser.settings
    STAT_DIR = getattr(analyser.settings, 'LID_STAT_FOLDER', getcwd())
except:
    STAT_DIR = getcwd()



def clean_punctuation_from_text(text):
    """Eliminates punctuation symbols from the submitted text."""
    for i in punctuation:
        if i in text:
            text = replace(text, i, " ")
    return text

def prepare_text(text):
    prepared_text = re.sub(r"\n", r" ", text)
    prepared_text = re.sub(r"\s+", r" ", prepared_text)
    return prepared_text


class Lid:
    """The basic class for Language Identification Library
    """

    def __init__(self):
        """Lid constructor
            The constructor loads automatically all language models in the
            current directory.
            The language models are stored in files that are made up as follows:
            LANGUAGE_NAME followd by .dat.
        """
        self.trigrams = Trigrams()
        self.languages  = [] # list of loaded language models
        self.models     = [] # list with the trigram models
        self.load_language_models()

    def load_language_models(self):
        for x in listdir( STAT_DIR ):
            if x[-4:] == ".dat":
                modelfile = file(os.path.join(STAT_DIR,x))
                language = x[0:-4]
                self.languages.append( language )
                new_model = Trigrams()
                for line in modelfile:
                    tokens = split(line)
                    if len(tokens) == 2:
                        trigram = lower( unicode( tokens[0],'utf-8') )
                        probability = float(tokens[1])
                        new_model.add_trigram(trigram,probability)
                self.models.append(new_model)
                modelfile.close()

    def checkText(self, text):
        """Check which language a text is."""
        self.trigrams.create_trigrams(text)
        self.trigrams.calculate_probabilities()
        result = self.count_deviation()
        language, confidence = find_best_language(self.languages, result)
        answer = {'confidence':confidence}
        stat = {}
        for x, lang in enumerate(self.languages):
            stat[lang] = result[x]
        answer['stat'] = stat
        return language, answer
#
#        if self.is_results_equal(result):
#            return '?', res

    def count_result_in_percents(results, num):
        new_result = [ float(result) / float(num) for result in results ]
        return new_result

    def count_deviation(self):
        result = []   
        for x in range(len(self.languages)):
            result.append(0)
        for x in self.trigrams.trigrams.keys():
            for i in range(len(self.models)):
                model = self.models[i]
                if model.trigrams.has_key(x):
                    value = model.trigrams[x] - self.trigrams.trigrams[x]
                    result[i] += abs( value )
                else:
                    # otherwise set the resulting value to 1 = max. deviation
                    result[i] += 1
        return result

    def is_results_equal(self,results):
        for x in range(len(results)-1):
            if results[x] != results[x+1]:
                return False
        return True


def find_best_language(languages, results):
        results = results[:]
        min_result = min(results)
        index = results.index(min_result)
        language = languages[index]
        results.sort()
        deviation = sum( [ (r-min_result)**2  for r in results[1:] ], 0 )
        max_deviation = sum( [ r**2  for r in results[1:] ], 0 )
        #print deviation, max_deviation
        confidence = float(deviation) / float(max_deviation)
        return language, confidence
      


if __name__ == "__main__":
    myLid = Lid()
    if len(sys.argv) > 1:
        for i in sys.argv[1:]:
            for y in glob.glob(os.path.normcase(i)):
                try:
                    lang, _ = myLid.checkText(open(y).read())
                    print "File:\t" + str(y) + "\tLanguage:\t" + lang
                except IOError:
                    print "Cannot open file:" + str(y)
                    pass
    else:
        print "Usage:"
        print "python Lid.py [filename]"

