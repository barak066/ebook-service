from math import log10

from djangosphinx.models import SphinxSearch

from django.db import models
from queryspell.trigram_tool import generate_trigram

DICTIONARY_NAME_LENGTH = 255
WORD_LENGTH = 255
TRIGRAM_LENGTH = 3
TRIGRAM_FIELD_LENGTH = WORD_LENGTH * (TRIGRAM_LENGTH + 1)

YES_NO_CHOICES = (
    ('y', 'yes'),
    ('n', 'no'),
)

class Dictionary(models.Model):
    name = models.CharField(max_length=DICTIONARY_NAME_LENGTH, unique=True)
    indexed_status = models.CharField(max_length=1, choices=YES_NO_CHOICES, default='n')
    
    def correct(self, query):
#        def cal_weight(base_length, word):
#            weight = word._sphinx['weight'] + 2 - abs(base_length - len(word.word)) + log10(word._sphinx['attrs']['frequency'])
#            return weight
        def correct_word(word):
            trigrams = u' '.join(generate_trigram(word))
            query_length = len(word)
            query_extended = '"%s"/2' % trigrams
    
            results = Words.search.query(query_extended)
            results = results.filter(dict_id=self.id)
            results = results.filter(length=range(query_length-2, query_length+3))
            #results = list(results)
            #results.sort(lambda x, y: \
            #    cmp(cal_weight(query_length, y), cal_weight(query_length, x)))
    
            if results:
                result = results[0].word
            else:
                result = word
            return result
        if query:
            query_words = query.split()
            corrected_words = [correct_word(word) for word in query_words]
            for first, second in zip(corrected_words, query_words):
                if first.lower() != second.lower:
                    return ' '.join(corrected_words)
        
    def __unicode__(self):
        return self.name

  


class Words(models.Model):
    word = models.CharField(max_length=WORD_LENGTH)
    trigrams = models.CharField(max_length=TRIGRAM_FIELD_LENGTH)

    length = models.IntegerField()
    frequency = models.IntegerField()
    dictionary = models.ForeignKey(Dictionary)

    class Meta:
        unique_together = ('word', 'dictionary')

    def __unicode__(self):
        string = "'%s' [freq %s] [dict %s]" % \
            (self.word, self.frequency, self.dictionary.name,)
        return string

    search = SphinxSearch(
        index='queryspell_index',
        mode='SPH_MATCH_EXTENDED2',
        rankmode='SPH_RANK_WORDCOUNT',
    )


#Dictionary.get(name='title').correct('liight')
