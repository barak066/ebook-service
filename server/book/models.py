try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

import urllib
import urlparse
import re
from urllib import quote

from django.db import models
from django.contrib import admin
from djangosphinx.models import SphinxSearch
from djangosphinx.apis.current import SPH_MATCH_ANY
from django.core.files import File
from django.conf import settings


from spec.langcode import LANG_CODE

NAME_LENGTH = 255
LINK_LENGTH = 4000
TEXT_LENGTH = 10000

AUTHOR_SHOW = (
    (0, 'always'),
    (1, 'admin'),
)

class BookFile(models.Model):
    link = models.TextField(max_length=LINK_LENGTH)
    link_hash = models.CharField(unique=True, max_length=32)
    time_found = models.DateTimeField(auto_now_add=True)
    last_check = models.DateTimeField(auto_now=True)

    size = models.IntegerField(default=0)
    type = models.CharField(max_length=10)
    more_info = models.TextField(max_length=TEXT_LENGTH, null=True, blank=True)
    img_link = models.TextField(max_length=LINK_LENGTH, null=True, blank=True)

    credit = models.IntegerField(default=0)

    def save(self, **kwargs):
        self.link_hash = md5(self.link).hexdigest()
        super(BookFile, self).save(kwargs)

    def __unicode__(self):
        return '%s [size %s] [type %s]' % (self.link, self.size, self.type)


class Series(models.Model):
    name = models.CharField(max_length=NAME_LENGTH, unique=True)

    def __unicode__(self):
        return self.name


class AuthorAlias(models.Model):
    name = models.CharField(max_length=NAME_LENGTH, unique=True)

    def __unicode__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=NAME_LENGTH, unique=True)
    credit = models.IntegerField(default=0)
    parent = models.ForeignKey('self', blank=True, null=True)

    def __unicode__(self):
        return self.name


class Language(models.Model):
    short = models.CharField(max_length=2, unique=True)
    full = models.CharField(max_length=255, unique=True)
    full_national = models.CharField(max_length=255)

    def __unicode__(self):
        return "%s" % ( self.full,)


class Author(models.Model):
    name = models.CharField(max_length=NAME_LENGTH, unique=True, null=False, blank=False)
    #book = models.ManyToManyField(Book, null=True, blank=True)#, limit_choices_to = {'id__lte': 0})
    #book = models.ManyToManyField(Book, null=True, blank=True, through='AuthorBook')#, limit_choices_to = {'id__lte': 0})
    alias = models.ManyToManyField(AuthorAlias, null=True, blank=True)
    tag = models.ManyToManyField(Tag, null=True, blank=True)
    info = models.TextField(null=True,blank=True)
    credit = models.IntegerField(default=0)

    #show = models.IntegerField(default=0, choices=AUTHOR_SHOW)

    # for more settings see 'spec/sphinx_conf/001_author_simple.tmplt'
    simple_search = SphinxSearch(
        index='authors_simple',
        weights={
            'name': 100,
        },
        mode='SPH_MATCH_ANY',
    )

    # for more settings see 'spec/sphinx_conf/002_author_soundex.tmplt'
    soundex_search = SphinxSearch(
        index='authors_soundex',
        weights={
            'name': 50,
        },
        mode='SPH_MATCH_ANY',
        morphology='soundex',
        limit=1000,
    )

    def __unicode__(self):
        return '[id %s] %s' % (self.id, self.name)
        
    def existed_books(self):
        return Author.objects.get(id=self.id).book.all()



#class AuthorBook(models.Model):
#    author = models.ForeignKey(Author)
#    book = models.ForeignKey(Book)
#
#    class Meta:
#        unique_together = (("book", "author"),)
#
#    def save(self, **kwargs):
#        super(AuthorBook, self).save(kwargs)
#        self.author.show = 0
#        self.author.save()
#
#    def delete(self):
#        print 'delete'
#        super(AuthorBook, self).delete()
#        if not self.author.book.count():
#            self.author.show = 1
#            self.author.save()




class Book(models.Model):
    title = models.CharField(max_length=NAME_LENGTH)
    lang = models.CharField(max_length=2, choices=LANG_CODE)
    language = models.ForeignKey(Language)
    book_file = models.ManyToManyField(BookFile, null=True, blank=True)
    series = models.ManyToManyField(Series, null=True, blank=True)
    tag = models.ManyToManyField(Tag, null=True, blank=True)
    credit = models.IntegerField(default=0)
    image = models.ImageField(upload_to="covers", null=True, blank=True)

    author = models.ManyToManyField(Author, null=True, blank=True)
    similar = models.ManyToManyField('self', null=True, blank=True, symmetrical=False)
    
    pagelink = models.TextField(max_length=LINK_LENGTH, null=True, blank=True)

    def add_tag(self, t):
        if t == None:
            return
        if t.credit == -2:
            self.add_tag(t.parent)
        if t.credit > 0 or t.credit == -1:
            self.tag.add(t)
            self.add_tag(t.parent)
            self.save()
        if t.credit == 0:
            self.tag.add(t)
            self.save()
    def add_tags(self, lst):
        for t in lst:
            self.add_tag(t)
    

    # for more settings see 'spec/sphinx_conf/003_book_title.tmplt'
    title_search = SphinxSearch(
        index='book_title',
        weights={
            'title': 100,
            'author': 50,
        },
        mode='SPH_MATCH_ANY'
    )

    def save(self, **kwargs):
# TODO add smart saving image there. Smart means don't make a copy of file with other name if it's exist. Also, generate thumbnail
#        if self.image:
#            url = self.image.url
#            if url[:7]=='http://':
#                _, netloc, link, _, _, _= urlparse.urlparse(url)
#                name = netloc + link
#                parts = name.split('.')
#                parts, ext = "".join(parts[:-1]), parts[-1]
#                name = parts.replace('-','_').replace('/','_').replace('.','_') + '.' + ext
#                #print url, name
#                result = urllib.urlretrieve(url)
#                content = result[0]
#                self.image.save(name,File(open(content)))
        super(Book, self).save(kwargs)

    def has_own_picture(self):
        return True if self.image and re.match("^covers/",self.image.url) else False

    def add_author(self, author_name):
        author, _ = Author.objects.get_or_create(name=author_name)
        self.author.add(author)

    def add_tag_name(self, tag_name):
        tag, _ = Tag.objects.get_or_create(name=tag_name)
        self.add_tag(tag)

    def add_bookfile(self, link, type):
        book_file, _= BookFile.objects.get_or_create(link=link,type=type)
        self.book_file.add(book_file)

    def set_lang(self, language):
        try:
            self.language = Language.objects.get(short=language)
        except Language.DoesNotExist:
            self.language, _ = Language.objects.get_or_create(short='?',
                            full='unknown', full_national='unknown')
        self.lang = self.language.short

    def add_annotation(self, annotation):
        annotation, _ = Annotation.objects.get_or_create(book=self,name=annotation)
        self.annotation_set.add(annotation)

    def book_authors(self):
        return Book.objects.get(id=self.id).author.all()


#    # for more settings see 'spec/sphinx_conf/004_book_title_author.tmplt'
#    title_author_search = SphinxSearch(
#        index='book_title_author',
#        weights={
#            'author_name': 100,
#        },
#        mode='SPH_MATCH_ANY',
#    )

#    # for more settings see 'spec/sphinx_conf/004_book_title_annotation.tmplt'
#    title_annotation_search = SphinxSearch(
#        index='book_title_annotation',
#        weights={
#            'title': 100,
#        }
#    )

    def __unicode__(self):
        return '[id %s] %s (%s)' % (self.id, self.title, self.lang)

    def get_book_files(self):
        book_files = []
        for book_file in self.book_file.all():
            if book_file.link.startswith("http://lib.ru"):
                file = BookFile()
                file.link = "/from/lib/ru/?link=" + quote(book_file.link)
                file.type = "epub+zip"
                book_files.append(file)

            book_files.append(book_file)
        return book_files


class EpubBook(models.Model):
    name = models.FileField(upload_to="./uploads/")
    book = models.ForeignKey(Book)


#class Annotation2(models.Model):
#    name = models.TextField()
#    book = models.ForeignKey(Book)
#
#    def __unicode__(self):
#        return '[id %s] %s' % (self.id, self.name)

class Annotation(models.Model):
    name = models.TextField()
    book = models.ForeignKey(Book)

    def __unicode__(self):
        return '[id %s] %s' % (self.id, self.name[0:20]+"...")
