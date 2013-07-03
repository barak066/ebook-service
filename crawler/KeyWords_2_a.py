# -*- coding: UTF-8 -*-

import Stemmer, re
stemmer = Stemmer.Stemmer('russian')

class KeyWords(object):
        
    def __init__(self, filename):
        self.keywords = {}
        self.words = self.keywords.viewkeys()
        self._dumped = True
        

    def add_kw(self, new_kw, file_name):
        word, weight = new_kw
        stemmed_word = stemmer.stemWord(word.lower())
        if stemmed_word in self.words:
            return
        else:
            self.keywords[unicode(stemmed_word)] = weight
            self.words = self.keywords.viewkeys()
        f = file( file_name, 'a')
        f.write( stemmed_word + ' : ' + str(weight) + '\n' )
        f.close()

    def load_keyword_list(self, filename):
        f = file(filename, 'r')
        fileContents = f.read().split('\n')
        f.close()
        if not fileContents[-1]:
            fileContents = fileContents[:-1]
        kwList = map( (lambda kw: tuple(kw.split(' : '))), fileContents )
        kwList = map( lambda kw: (unicode(kw[0].decode('utf8')), int(kw[1])), kwList )
        self.keywords = dict(kwList)
        return

    def get_word_weight(self, word):
        return self.keywords.get(stemmer.stem(word), 0)

