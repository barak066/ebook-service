# -*- coding: utf-8 -*-

from analyser.core.tasking import BaseTask
from analyser.core.tasking.standard_tasks import BookSavingTask
from analyser.adds.helpers import make_correct_link

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
        tasks = [ BigGenreTask( make_correct_link(self.link, link)) for link in Retriever.get_genres_links(soup) ]
        self.tasks = tasks
        return True

class BigGenreTask(BaseTask):
    def __init__(self, link):
        BaseTask.__init__(self)
        self.link = link
        self.weight = 20
        self.need_html = True

    def __repr__(self):
        return '<BigGenreTask: %s>' % self.link

    def execute(self,html):
        soup = get_soup(html)
        tasks = [ GenreTask( make_correct_link(self.link, glink)) for glink in Retriever.get_genres_links(soup) ]
        self.tasks = tasks
        return True

class GenreTask(BaseTask):
    def __init__(self, link):
        BaseTask.__init__(self)
        self.link = link
        self.weight = 15
        self.need_html = True

    def __repr__(self):
        return '<GenreTask: %s>' % self.link

    def execute(self,html):
        soup = get_soup(html)
        links = [ self.link ]
        links += Retriever.get_link_pages(soup, self.link)
        self.tasks = [ BookListingTask(link) for link in links ]
        return True

class BookListingTask(BaseTask):
    def __init__(self,link):
        BaseTask.__init__(self)
        self.link = link
        self.weight = 10
        self.need_html = True

    def __repr__(self):
        return '<BookListingTask: %s>' % self.link

    def execute(self,html):
        soup = get_soup(html)
        links = [make_correct_link(self.link, book_link) for book_link in Retriever.get_book_links(soup) ]
        self.tasks = [ GetBookInfoTask( link) for link in links]
        return True

class GetBookInfoTask(BaseTask):
    def __init__(self, link):
        BaseTask.__init__(self)
        self.link = link
        self.weight = 5
        self.need_html = True

    def __repr__(self):
        return '<GetBookInfoTask: %s>' % self.link

    def execute(self,html):
        soup = get_soup(html)
        book_info = Retriever.correct_book_info( Retriever.get_book_info(soup), self.link)
        self.tasks = [ BookSavingTask(book_info) ]
        return True