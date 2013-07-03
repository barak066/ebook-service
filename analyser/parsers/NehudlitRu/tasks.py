# -*- coding: utf-8 -*-

from analyser.core.tasking import BaseTask
from analyser.core.tasking.standard_tasks import BookSavingTask
from Retriever import Retriever
from analyser.parsers import get_soup

class InitialTask(BaseTask):
    def __init__(self, site_link):
        BaseTask.__init__(self)
        self.weight = 10
        self.need_html = True
        self.link = site_link

    def __repr__(self):
        return '<initial task>'

    def execute(self, html):
        soup = get_soup(html)
        queue = Retriever.get_queue(soup)
        Retriever.correct_queue(queue, self.link)
        tasks = [ GetBookInfoTask(q['tags'], q['link']) for q in queue ]
        self.tasks = tasks
        return True

class GetBookInfoTask(BaseTask):
    def __init__(self, tags, link):
        BaseTask.__init__(self)
        self.weight = 10
        self.need_html = True
        self.link = link
        self.tags = tags

    def __repr__(self):
        return '<GetBookInfoTask: %s>' % self.link

    def execute(self,html):
        soup = get_soup(html)
        book_info = Retriever.get_book_info(soup)
        book_info.tags = self.tags
        book_info.pagelink = self.link
        self.tasks =  [ BookSavingTask(book_info) ]
        return True