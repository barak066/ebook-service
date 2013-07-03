import codecs

from django.core.management.base import BaseCommand

import settings

from queryspell.models import Dictionary, Words
from queryspell.trigram_tool import generate_trigram
from queryspell.generate_conf import generate_sphinx_conf

class Command(BaseCommand):
    option_list = BaseCommand.option_list
    help = 'Load data from file to dictionary.'
    args = 'dictname filename'

    usage_str = 'Usage: manage.py loaddict [options] dictname filename'

    requires_model_validation = False


    def handle(self, dictname=None, filename=None, **options):
    

        if not dictname:
            print 'You must name dictionary for loading data'
            print self.usage_str
            return

        if not filename:
            print 'Please provide a file with data for reading'
            print self.usage_str
            return

        error_message = self.__load_data(dictname, filename)
        if error_message:
            print error_message
            return
            
        self.__generate_sphinx_conf()


    def __load_data(self, dictname, filename):
        dictionary, is_created = Dictionary.objects.get_or_create(name=dictname)
        if not is_created:
            print 'Removing old data from dictionary ...'
            Words.objects.filter(dictionary=dictionary).delete()

        line = ''
        added_word_count = 0
        try:
            in_file = codecs.open(filename, mode='r', encoding='utf-8')
            
            print 'Loading new data ...'

            for line_count, line in enumerate(in_file):
                if line:
                    word, freq = line.split()
                    if not word.isdigit():
                        added_word_count += 1
                        word = word.lower()
                        trigrams = u' '.join(generate_trigram(word))
                        Words.objects.create(word=word, trigrams=trigrams, \
                                             length=len(word), frequency=freq, \
                                             dictionary=dictionary)

        except ValueError, ex:
            return "Error in %s line: bad file format (%s)\n`%s'" % \
                   (line_count, ex, line)
        finally:
            in_file.close()

        print 'Complete: %s word(s) loaded into dict' % added_word_count
        

    def __generate_sphinx_conf(self):
        SPHINX_CONF_FILE = getattr(settings, 'QUERYSPELL_SPHINX_CONF_FILE', \
                                   './queryspell_sphinx.conf')
        sphinx_conf_str = generate_sphinx_conf()
        out_file = codecs.open(SPHINX_CONF_FILE, mode='w', encoding='utf8')
        out_file.write(sphinx_conf_str)
        out_file.close()
            
