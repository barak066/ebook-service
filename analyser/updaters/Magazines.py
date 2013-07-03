#!/usr/bin/env python
# -*- coding: utf-8 -*-
from server.django.db.models.query_utils import Q

from server.magazines.models import Article,Category, Issue, Magazine
from analyser.core.tasking.standart_tasks import standart_tasks
from analyser.parsers.Magazines.Preprocessor import Preprocessor

REPLACES = Preprocessor.REPLACES


class InitialTask(standart_tasks):
    def __init__(self):
        standart_tasks.__init__(self)
    def __repr__(self):
        return '<InitialTask Magazine updater>'
    def execute(self):
        query = Q(title__contains = REPLACES[REPLACES.keys()[0]])
        for what in REPLACES.keys()[1:]:
            query = query | Q(title__contains=what)
        articles = Article.objects.filter(query)
        self.tasks = [ ChangerTask(article.id) for article in articles]
        return True


class ChangerTask(standart_tasks):
    def __init__(self,id):
        standart_tasks.__init__(self)
        self.id = id
    def __repr__(self):
        return '<ChangerTask %d>' % self.id
    def execute(self):
        article = Article.objects.get(id=self.id)
        article.title = Preprocessor.change_strange_symbols(article.title)
        article.save()
        return True

