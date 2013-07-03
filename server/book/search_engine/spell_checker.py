# -*- coding: utf-8 -*-

import logging
try:
    any2 = any
except NameError:
    def any2(iterable):
        "Implementation builtin function 'any'"
        for element in iterable:
            if element:
                return True
        return False

#from spec.external.aspell import Speller, AspellSpellerError
try:
    from settings import ASPELL_DICTIONARIES
except ImportError:
    ASPELL_DICTIONARIES = None

MAIN_LOG = logging.getLogger("main_logger")


def recognize_lang(query):
    "Tries to recognize language, returns 2 letters code."
    russian_letters = \
        u'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    if any2( (letter in russian_letters for letter in query) ):
        return 'ru'
    else:
        return 'en'


def spell_check(query, lang=None):
    "Chekces spelling using lang or tries to recognize language."
    if not query:
        return
    # TODO add capital russian letters for recognizing language
#    try:
#        # TODO should i recognize language for hole query or for each word?
#        if not lang:
#            lang = recognize_lang(query)
#        speller_options = [('lang', lang), ('encoding', 'utf-8')]
#        if ASPELL_DICTIONARIES:
#            speller_options.append(('data-dir', ASPELL_DICTIONARIES))
#        speller = Speller(*speller_options)
#        correct_words = []
#        corrected = False
#
#        if isinstance(query, unicode):
#            query = query.encode('utf-8')
#
#        for word in query.split():
#            if speller.check(word):
#                correct_words.append(word)
#            else:
#                correct_word = speller.suggest(word)
#                if correct_word:
#                    corrected_word = correct_word[0]
#                    correct_words.append(corrected_word)
#                    if word.lower() != corrected_word.lower():
#                        corrected = True
#                else:
#                    correct_words.append(word)
#
#        if corrected:
#            return unicode(' '.join(correct_words), 'utf-8')
#               
#    except AspellSpellerError, ex:
#        MAIN_LOG.warning("aspell error: %s" % ex)
        
