# -*- coding: utf-8 -*-

"in this package: Info classes, that's using by parser for site's information (about book or etc) grabbing"

class Info:
    def __str__(self):
       return self.to_string()

    def to_string(self):
        return self._make_strings( self._get_full() )

    def simple_string(self):
        return self._make_one_string( self._get_short() )

    def _get_full(self):
        return [ ('FullBase' , 'base') ]

    def _get_short(self):
        return [ ('Short base' , 'base') ]

    def _get_str(self, text):
        s = text
        if not text:
            return ''
        if type(text) == str:
            s = unicode(text,'utf-8', errors='ignore')
        elif type(text) == list:
            s = self._get_str(" %%%".join(text))
        elif type(text) == dict:
            s = u''
            for k,v in text:
                s += '%s : %s' % (k, self._get_str(text))
        elif type(text) == int:
            s = str(text)
        elif type(text) == unicode:
            pass
        return s

    def _make_strings(self,from_what):
        string = u''
        for title, text in from_what:
            string += '%s : %s\n' % (title, self._get_str(text))
        return string

    def _make_one_string(self,from_what):
        string = u''
        for title, text in from_what:
            string += '%s : %s; ' % (title, self._get_str(text))
        return string


