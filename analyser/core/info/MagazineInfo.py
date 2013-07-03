# -*- coding: utf-8 -*-

from . import Info

class MagazineInfo(Info):
    def __init__(self):
        self.name = ""
        self.about = ""
        self.cover = ""
        self.description = ""
        self.link  = ""

    def _get_full(self):
        return [('Name' , self.name),
                ('About' , self.about),
                ('Description' , self.description),
                ('Cover' , self.cover),
                ('Link' , self.link),
               ]


    def _get_short(self):
        return [ ('Name' , self.name),
                ('Link' , self.link),
               ]
        