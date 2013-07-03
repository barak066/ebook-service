# -*- coding: utf-8 -*-

from analyser.core.tasking import BaseTask
from analyser.core.tasking.standard_tasks import BookSavingTask
from analyser.adds.helpers import make_correct_link
from analyser.adds import logger
from Retriever import Retriever
from lib.BeautifulSoup.BeautifulSoup import BeautifulSoup


class Page(BaseTask):
    def __init__(self, link):
        BaseTask.__init__(self)
        self.weight = 20
        self.need_html = True
        self.link = link

    def __repr__(self):
        return '<Page: %s>' % self.link

    def execute(self, html):
        data, page = html
        soup = BeautifulSoup(data,convertEntities=BeautifulSoup.XML_ENTITIES, fromEncoding='utf-8')
        if Retriever.is_acquisition_feed(soup):
            self.tasks = [ Entry(unicode(entry), self.link) for entry in Retriever.get_entries(soup) ]
        else: #navigation feed
            entries = Retriever.get_entries(soup)
            links = filter( lambda l: l!=None, [Retriever.get_catalog_link(entry) for entry in entries] )
            links = filter( Retriever.is_permitted_link, links)
            links = map( lambda link: make_correct_link(self.link, link), links)
            self.tasks = [ Page(link) for link in links]
        return True

class Entry(BaseTask):
    def __init__(self, unicode_entry, pagelink):
        BaseTask.__init__(self)
        self.weight = 1
        self.entry = unicode_entry
        self.link = pagelink

    def __repr__(self):
        return '<Entry: %s>' % self.link

    def execute(self):
        entry = BeautifulSoup(self.entry,convertEntities=BeautifulSoup.XML_ENTITIES)
        bookinfo = Retriever.get_bookinfo(entry)
        if not bookinfo:
            logger.write_fail("empty links at entry",entry=entry, link=self.link)
            return True
        bookinfo.pagelink = self.link
        for format, link in bookinfo.links.items():
            bookinfo.links[format] = make_correct_link(self.link, bookinfo.links[format] )
        self.tasks = [ BookSavingTask(bookinfo) ]
        return True
