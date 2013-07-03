# -*- coding: utf-8 -*-

from analyser.core.tasking import BaseTask
from analyser.core.tasking.standard_tasks import BookSavingTask
from analyser.adds.helpers import make_correct_link
from Retriever import Retriever
from server.magazines.models import Magazine, Article, Category, Issue
from analyser.parsers import get_soup

class InitialTask(BaseTask):
    def __init__(self, site_link):
        BaseTask.__init__(self)
        self.weight = 20
        self.need_html = True
        self.link = site_link

    def __repr__(self):
        return '<InitialTask: %s>' % self.link

    def execute(self, html):
        soup = get_soup(html)
        links_magazines = Retriever.get_links_on_magazines(soup)
        links_magazines = [make_correct_link(self.link, link) for link in links_magazines]
        self.tasks = [ MagazineInfoTask( link ) for link in links_magazines]
        return True


class MagazineInfoTask(BaseTask):
    def __init__(self, link):
        BaseTask.__init__(self)
        self.weight = 10
        self.need_html = True
        self.link = link

    def __repr__(self):
        return '<MagazineInfoTask:  %s>' % self.link

    def execute(self, html):
        soup = get_soup(html)
        magazine_info = Retriever.get_magazine_info(soup)
        magazine_info.cover = make_correct_link(self.link, magazine_info.cover)
        magazine_info.link = self.link
        issue_links = [ make_correct_link(self.link, link) for link in Retriever.get_links_magazine_issue(soup) ]
        self.tasks = [ MagazineIssueTask( magazine_info.name, issue_link) for issue_link in issue_links ]
        self.tasks += [ MagazineSavingTask( magazine_info ) ]
        return True

class MagazineIssueTask(BaseTask):
    def __init__(self, magazine, link):
        BaseTask.__init__(self)
        self.weight = 5
        self.need_html = True
        self.link = link
        self.magazine = magazine

    def __repr__(self):
        return '<MagazineIssueTask:  %s>' % self.link

    def execute(self, html):
        soup = get_soup(html)
        year, number = Retriever.get_issue_year_number_by_link(self.link)
        articles = Retriever.get_issue_articles(soup)
        for article in articles:
            article.magazine = self.magazine
            article.year = year
            article.number = number
            article.link = make_correct_link(self.link, article.link)
            article.link = Retriever.print_version(article.link)
        self.tasks = [ArticleSavingTask(article) for article in articles]
        return True



class ArticleSavingTask(BaseTask):
    def __init__(self, article):
        BaseTask.__init__(self)
        self.article_info = article
        self.weight = -100
        self.longterm = True

    def __repr__(self):
        return '<ArticleSavingTask >'# % self.article_info.simple_string()

    def execute(self):
        #Preprocessor.article_info(self.article_info)
        magazine, _ = Magazine.objects.get_or_create(name=self.article_info.magazine)
        issue, _ = Issue.objects.get_or_create(magazine=magazine,
                                               number= int(self.article_info.number),
                                               year = int(self.article_info.year) )
        article, _ = Article.objects.get_or_create(link=self.article_info.link,
                                                   issue=issue,
                                                   title = self.article_info.title)
        if self.article_info.category:
            article.category = [ Category.objects.get_or_create(name=self.article_info.category)[0] ]
        article.description = self.article_info.description if self.article_info.description else None
        article.authors = self.article_info.authors if self.article_info.authors else None
        article.save()
        return True


class MagazineSavingTask(BaseTask):
    def __init__(self, magazine_info):
        BaseTask.__init__(self)
        self.magazine_info = magazine_info
        self.weight = -150
        self.longterm = True

    def __repr__(self):
        return '<MagazineSavingTask:  %s>' % self.magazine_info.link

    def execute(self):
        #Preprocessor.magazine_info(self.magazine_info)
        magazine, _ = Magazine.objects.get_or_create(name=self.magazine_info.name)
        magazine.about = self.magazine_info.about
        magazine.cover = self.magazine_info.cover
        magazine.description = self.magazine_info.description
        magazine.link  = self.magazine_info.link
        magazine.save()
        return True

