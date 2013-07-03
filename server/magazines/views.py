# -*- coding: utf-8 -*-
from server.django.shortcuts import render_to_response
from models import Magazine, Issue, Category

from server.django.http import HttpResponseRedirect
from server.django.conf import settings
from server.django.http import Http404

from epuber.magazines import MagazineParser
from epuber.epub import BookProperties
import tempfile
import shutil
import os
from urllib import quote

class Feed:
    def __init__(self, title, self_link):
        self.entries = []
        self.title = title
        self.self_link = self_link
    pass

class Link():
    def __init__(self, **kwargs):
        self.atts = {}
        for k,v in kwargs.items():
            self.atts[k] = v
    def atts_get(self):
        if 'type' in self.atts:
            yield ('type', self.atts['type'])
        if 'href' in self.atts:
            yield ('href', self.atts['href'])
        if 'rel' in self.atts:
            yield ('rel', self.atts['rel'])
    def show_params(self):
        s = ''
        if 'type' in self.atts:
            s += 'type=%s ' % self.atts['type']
        if 'href' in self.atts:
            s += 'href=%s ' % self.atts['href']
        if 'rel' in self.atts:
            s += 'rel=%s ' % self.atts['rel']
        print s
        return s

class Entry:
    def __init__(self):
        self.title = ''
        self.links = []
        self.updated = ''
        self.id = ''
        self.content = ''
        pass


def index(request):
    feed = Feed()
    entry = Entry()
    entry.title = 'Magazines'
    entry.id='/magazines/list/'
    entry.links.append( Link(href=entry.id, type='application/atom+xml'))
    entry.content = 'Alpha index of magazines'
    feed.entries.append(entry)
    return render_feed(feed)


def list(request):
    magazines = Magazine.objects.exclude(issue__isnull=True).order_by('name')
    feed = Feed('EbooksSearch Magazines', request.path)
    for magazine in magazines:
        entry = Entry()
        entry.title=magazine.name
        entry.id = "%s%d" % (request.path, magazine.id)
        entry.links.append( Link(href=entry.id, type='application/atom+xml'))
        if magazine.cover:
            entry.links.append( Link(href=magazine.cover.url, type='image/jpeg', rel="http://opds-spec.org/image/thumbnail"))
        entry.content = magazine.about
        feed.entries.append(entry)
    return render_feed(feed)

def show_years(request, magazine_id):
    magazine = Magazine.objects.get(id=magazine_id)
    issues = magazine.issue_set.all()
    years = {}
    for issue in issues:
        if issue.year in years:
            years[issue.year] += 1
        else:
            years[issue.year] = 1
    years_list = [(k, v) for k,v in years.items()]
    years_list.sort(key=lambda x: x[0], reverse=True)
    feed = Feed(u'Список по годам', request.path)
    for year, n in years_list:
        entry = Entry()
        entry.title = u'%s, %d год' % (magazine.name, year)
        entry.id = '%s%d/' % (request.path, year)
        entry.links.append( Link(href=entry.id, type='application/atom+xml'))
        entry.content = u"Количество выпусков: %d" % n
        feed.entries.append(entry)
    return render_feed(feed)


def show_issues(request, magazine_id, year):
    magazine = Magazine.objects.get(id=magazine_id)
    issues = magazine.issue_set.filter(year=year).order_by('number')
    feed = Feed("Список выпусков журналов", request.path)
    for issue  in issues:
        entry = Entry()
        entry.title = u'%s №%d (%d год)' % (issue.magazine.name, issue.number, issue.year)
        entry.id = '%s%d/' % (request.path, issue.number)
        entry.links.append(Link(href="/magazines/generate/%d"%issue.id, type="application/epub+zip", rel="http://opds-spec.org/acquisition"))

        articles = issue.article_set.all()
        other = u'другое'
        categories = { other : 0}
        for article in articles:
            try:
                c = article.category.get()
                if c.name in categories:
                    categories[c.name] += 1
                else:
                    categories[c.name] = 1
            except Category.DoesNotExist:
                categories[other] += 1
        if categories[other] == 0:
            categories.pop(other)
        names= [ u"%s (%d)" % (name, count) for name,count in categories.items()  ]
        entry.content = u"Количество статей: %d" % issue.article_set.count()
        add_content = u"\n".join( names  )
        entry.content += u".\nПо рубрикам:\n"+add_content
        #
        feed.entries.append(entry)
    return render_feed(feed)

def generate_epub(request, id):
    try:
        issue = Issue.objects.get(id=id)
    except Issue.DoesNotExist:
        raise Http404
    name = u"Журнал %s №%d за %d год" % (issue.magazine.name, issue.number, issue.year)
    folder = 'magazines'
    link_name =  settings.MEDIA_URL + "/%s/%s/" % (settings.MEDIA_DOWNLOAD_FOLDER, folder) + quote(name.encode('utf-8')) + ".epub"
    book_folder = os.path.join(settings.MEDIA_ROOT,settings.MEDIA_DOWNLOAD_FOLDER, folder)
    if not os.path.exists(book_folder):
        os.makedirs(book_folder)
    book_name = os.path.join(book_folder, name.encode("utf-8") + ".epub")
    if not os.path.exists(book_name):
        temp_name = tempfile.mkstemp()
        properties = BookProperties(temp_name[1], name)
        properties.language = "ru"
        properties.genre = "magazine"
        magazine_parser = MagazineParser(issue, properties)
        magazine_parser.parse()
        magazine_parser.create_book()
        shutil.copy(temp_name[1], book_name)
        os.chmod(book_name, 0666)

    return HttpResponseRedirect("/" + link_name)


def show_articles(request, magazine_id, year, number):
    issue = Issue.objects.get(magazine=magazine_id, year=year, number=number)
    feed = Feed('Articles', request.path)
    for article in issue.article_set.all():
        entry = Entry()
        entry.title = article.title
        entry.id = article.link
        entry.links.append( Link(href=entry.id, type="application/html", rel="http://opds-spec.org/acquisition"))
        entry.links.append( Link(href=entry.id, type="text/html", rel="alternate"))
        entry.content = "Category: %s" % article.category.get().name
        feed.entries.append(entry)
    return render_feed(feed)


def render_response_atom(*args, **kwargs):
    kwargs['mimetype'] = "application/atom+xml"
    return render_to_response(*args, **kwargs)

def render_feed(feed):
    return render_response_atom('opds/feed.xml', {'feed':feed})

