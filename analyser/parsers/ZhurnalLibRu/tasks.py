# -*- coding: utf-8 -*-

from analyser.core.tasking import BaseTask
from analyser.core.tasking.standard_tasks import BookSavingTask
from analyser.adds.helpers import make_correct_link
from Retriever import Retriever
from analyser.parsers import get_soup

class InitialTask(BaseTask):
    def __init__(self, site_link):
        BaseTask.__init__(self)
        self.weight = 20
        self.need_html = True
        self.link = site_link

    def __repr__(self):
        return '<initial task>'

    def execute(self, html):
        soup = get_soup(html)
        genres = Retriever.get_genres(soup)
        for genre in genres:
            genre['link'] = make_correct_link(self.link, genre['link'])
        self.tasks = [ GetAllPagesGenre(g['link'],g['name']) for g in genres ]
        return True

class GetAllPagesGenre(BaseTask):
    def __init__(self, link, genre):
        BaseTask.__init__(self)
        self.weight = 10
        self.need_html = True
        self.link = link
        self.genre = genre
        
    def __repr__(self):
        return '<GetAllPagesGenre: %s>' % self.link

    def execute(self,html):
        soup = get_soup(html)
        number = Retriever.get_pages_number(soup)
        pagelinks = Retriever.generate_all_pagelinks_for_genre(self.link, number)
        self.tasks = [ GenrePage(link, self.genre) for link in pagelinks]
        return True

class GenrePage(BaseTask):
    def __init__(self, link, genre):
        BaseTask.__init__(self)
        self.weight = 5
        self.need_html = True
        self.link = link
        self.genre = genre

    def __repr__(self):
        return '<GenrePage: %s>' % self.link

    def execute(self,html):
        soup = get_soup(html)
        bookinfos = [ Retriever.postprocess_bookinfo(raw_bookinfo,self.link, self.genre)  \
                      for raw_bookinfo in  Retriever.get_bookinfos(soup)  ]
        self.tasks = [ BookSavingTask(book_info) for book_info in bookinfos ]
        return True

