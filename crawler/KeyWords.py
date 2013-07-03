# -*- coding: UTF-8 -*-
__author__ = 'pxanych'

class KeyWords(object):
    key_words = {}
    words = key_words.viewkeys()

    @classmethod
    def add_kw ( cls, new_kw, file_name ):
        if new_kw[0] in cls.words:
            return
        else:
            cls.key_words[unicode(new_kw[0])] = new_kw[1]
            cls.words = cls.key_words.viewkeys()
        f = file( file_name, 'a')
        f.write( new_kw[0] + ' : ' + str(new_kw[1]) + '\n' )
        f.close()

    @classmethod
    def load_kw ( cls, file_name ):
        f = file(file_name, 'r')
        fileContents = f.read().split('\n')
        f.close()
        if not fileContents[-1]:
            fileContents = fileContents[:-1]
        kwList = map( (lambda kw: tuple(kw.split(' : '))), fileContents )
        kwList = map( lambda kw: (unicode(kw[0].decode('utf8')), int(kw[1])), kwList )
        
        cls.key_words = dict(kwList)
        cls.words = cls.key_words.viewkeys()
        return

    @classmethod
    def load_link_kw ( cls, file_name = 'dict_LinkKW' ):
        cls.load_kw( file_name )
        return
