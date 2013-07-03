import re
# -*- coding: utf-8 -*-
import Stemmer
en_stemmer = Stemmer.Stemmer('english')
ru_stemmer = Stemmer.Stemmer('russian')

class Analyzer:
    '''
    Base class.
    Used for changing and saving.
    To use any analyzer, stopwords are desirable to be initialized with read_stopwords()
    '''

    stopwords = []

    def __init__(self):
        self.data = ''
        self.words = []
        self.lang = 'ru'

    def read_string(self, sdata):
        '''Reads string to self.data'''
        self.data = (sdata)

    def get_words(self):
        pass

class TextAnalyzer(Analyzer):
    '''
    Analyzes single words
    '''
    def __init__(self):
        self.data = ''
        self.words = []
        self.lang = 'ru'

    def get_words(self):
        '''Makes word list from self.data'''
        splitter=re.compile('''[^\w|']|[0-9]+''', re.U)
        raw_words = [s.lower( ) for s in splitter.split(self.data)]
        self.words = []
        for w in raw_words:
            if w != '':
                if self.lang == 'ru':
                    w = ru_stemmer.stemWord(w)
                if self.lang == 'en':
                    w = en_stemmer.stemWord(w)
                if (w not in Analyzer.stopwords + self.words):
                    self.words.append(w)

class PairAnalyzer(Analyzer):
    '''
    Analyzes word pairs
    '''
    def __init__(self):
        self.data = ''
        self.words = []
        self.lang = 'ru'

    def get_words(self):
        '''Makes pair list from self.data'''
        sent_splitter=re.compile('''[\.?!]+''', re.U)
        splitter = re.compile('''[^\w|']|[0-9]+''', re.U)
        sentences = [s.lower( ) for s in sent_splitter.split(self.data)]
        raw_words_list = []
        for sent in sentences:
            raw_words_list.append([s.lower( ) for s in splitter.split(sent)])
        self.words = []
        rw = []
        for sent_words in raw_words_list:
            temp = []
            for w in sent_words:
                if w != '':
                    if self.lang == 'ru':
                        w = ru_stemmer.stemWord(w)
                    if self.lang == 'en':
                        w = en_stemmer.stemWord(w)
                    if (w not in Analyzer.stopwords):
                        temp.append(w)
            rw.append(temp)
        for sent_words in rw:
            pairs = zip(sent_words[:], sent_words[1:])
            for p in pairs:
                if p not in self.words:
                    self.words.append(p[0] + ' ' + p[1])

def read_stopwords():
    '''
    Initializes Analyzer.stopwords
    '''
    inp=open('stopwords/RU_List', 'r')
    swfiles = inp.readlines()
    stopwords = []
    stopwords1 = []
    for f in swfiles:
        inp1=open('stopwords/' + f[0:len(f)-1], 'r')
        stopwords += inp1.readlines()
    for w in stopwords:
        w1 = w[0:len(w)-1]
        w1 = ru_stemmer.stemWord(w1)
        w1 = unicode(w1.decode('UTF-8'))
        if w1 not in stopwords1:
            stopwords1.append(w1)
    Analyzer.stopwords = stopwords1

class Classifier:
    '''
    Saves information for one word in one genre
    '''

    def __init__(self):
        self.nonzero = 0
        self.num = 0

    def set_data(self, nonzeronum, allnum):
        self.num = allnum
        self.nonzero = nonzeronum

def getProbability(group_cl, all_cl):
    '''
    Returns probability and weight for tag, corresponding to group.cl
    weight is almost useless now
    '''
    if group_cl == None:
        if all_cl == None:
            return [0.5, 0]
        return [0, 1]
    prob = 1.0 * group_cl.nonzero * all_cl.num / (all_cl.nonzero * group_cl.num + group_cl.nonzero * all_cl.num)
    weight = 1
    return [prob, weight]

