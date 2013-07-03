# -*- coding: utf-8 -*-
from analyser.core.info.BookInfo import BookInfo

from analyser.core.tasking import BaseTask, NeedHTMLTask
from analyser.core.tasking.standard_tasks import BookSavingTask

from analyser.adds.helpers import make_correct_link
from Retriever import Retriever
from Preprocessor import  Preprocessor
from analyser.parsers import get_soup, get_text
from lib.chardet.universaldetector import UniversalDetector
from lib.lid.lid import Lid
from analyser.adds import logger
import analyser.settings

LANG_ID = Lid()


class DirPage(NeedHTMLTask):
    def __init__(self, link):
        super(DirPage,self).__init__(link)
        self.weight = 10
        self.link = link

    def execute(self, html):
        soup = get_soup(html)
        dirs = Retriever.get_accept_dirs(soup, self.link)
        books = Retriever.get_accept_books(soup, self.link)
        self.tasks = [ DirPage( link )  for link,_ in dirs ]
        self.tasks += [ BookPage( link+'_Ascii.txt' ) for link,_ in books ]
        return True

class BookPage(NeedHTMLTask):
    def __init__(self, link):
        super(BookPage,self).__init__(link)
        self.weight = 5

    def execute(self, html):
        text = get_text(html)
        bi = self.retrieve(text)
        bi = BookPage.preprocess(bi)
        if bi.language == '?':
            bi.language = BookPage.define_lang(text)
        self.tasks = [ BookSavingTask(bi) ]
        return True

    def retrieve(self,text):
        bi = BookInfo()
        bi.authors, bi.title = Retriever.get_authors_and_title(text)
        bi.pagelink = self.link
        bi.links['txt'] = self.link
        tag = Retriever.get_tag_by_link(self.link)
        bi.tags = [tag] if tag else []
        return bi

    @staticmethod
    def define_lang(text):
        language, confidence = LANG_ID.checkText(text)
        return language

    @staticmethod
    def preprocess(bi):
        bi.title = Preprocessor.cleanup_year(bi.title)
        bi.authors = map( lambda author: Preprocessor.cleanup_year(author),  bi.authors )
        bi.language = Preprocessor.guess_lang_by_link( bi.links['txt'] )
        bi.title = Preprocessor.cleanup_kilobytes(bi.title)
        return bi
