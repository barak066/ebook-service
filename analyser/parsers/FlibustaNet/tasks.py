# -*- coding: utf-8 -*-
from analyser.core.info.BookInfo import BookInfo

from analyser.core.tasking import BaseTask
from analyser.adds.helpers import make_correct_link
from analyser.core.tasking.standard_tasks import BookSavingTask
from analyser.parsers import get_soup
from Retriever import Retriever
from analyser.parsers import get_soup
from  analyser import settings
import urllib
import os
from lib.zipfile import ZipFile

#TODO add sintax sugar (for instance,NeedHTML) for task setting

class InitialTask(BaseTask):
    def __init__(self):
        BaseTask.__init__(self)
        self.weight = 20

    def __repr__(self):
        return '<InitialTask>'

    def execute(self):
        filepath = os.path.join(settings.path_to_project, settings.analyser, settings.data)
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        filename = os.path.join(filepath,'catalog.zip')
        urllib.urlretrieve('http://www.flibusta.net/catalog/catalog.zip', filename)
        self.tasks = [ GetNewId(1) ] # 1 because miss first line
        return True

class GetNewId(BaseTask):
    def __init__(self, start_line):
        BaseTask.__init__(self)
        self.weight = 15
        self.start_line = start_line

    def __repr__(self):
        return '<GetNewId: %d>' % self.start_line

    def execute(self):
        self.tasks = []
        filename = os.path.join(settings.path_to_project, settings.analyser, settings.data, 'catalog.zip')
        zip_file = ZipFile(filename)
        catalog_file = zip_file.open('catalog.txt')
        for i in xrange(self.start_line):
            catalog_file.readline()
        N_IDS = 20 #number of reading ID's
        for n in range(N_IDS):
            description_line = catalog_file.readline()
            if description_line == '':
                break #end of file
            description = Retriever.read_description(description_line)
            self.tasks.append( GetBookInfoTask('http://flibusta.net/b/%s' % description['ID'], description)  )
        if catalog_file.readline() != '':
            self.tasks.append( GetNewId(self.start_line+N_IDS))
        return True

class GetBookInfoTask(BaseTask):
    def __init__(self, link, description):
        BaseTask.__init__(self)
        self.weight = 10
        self.description = description
        self.link = link
        self.need_html = True

    def __repr__(self):
        return '<GetBookInfoTask: %s, %s>' % (self.description['ID'], self.link)

    def execute(self,html):
        soup = get_soup(html)
        book_info = BookInfo()
        book_info.title  = self.description['title']
        book_info.authors = [ "%s %s %s" % (self.description['firstname'],self.description['middlename'], self.description['lastname']) ]
        book_info.pagelink = self.link
        book_info.language = self.description['language']
        book_info.summary = Retriever.get_summary(soup)
        book_info.links = Retriever.get_links(soup, self.link)
        book_info.tags = Retriever.get_tags(soup)
        book_info.image = Retriever.get_picture(soup, self.link, self.description['ID'])
        self.tasks = [ BookSavingTask(book_info) ]
        return True



