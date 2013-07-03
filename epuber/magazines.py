#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
Module for creating magazines 
"""

__author__ = 'dima'

import os, sys, shutil
import re, string
import urllib

if not '..' in sys.path:
    sys.path.append('..')
if not '../server' in sys.path:
    sys.path.append('../server')
os.environ['pwd'] = '../server'
from django.core.management import setup_environ
from server import settings

setup_environ(settings)

from lib.BeautifulSoup.BeautifulSoup import *
from lib import chardet
from epub import Book, BookProperties, Category
import prettify

from django.core.files.uploadedfile import UploadedFile
import tempfile
try:
    from epuber.local_settings import *
except:
    pass

from analyser.parsers.Magazines.Preprocessor import Preprocessor

class MagazineParser:
    """
    Class for magazines to epub.
    """
    HTML_HEADER = """
    <html>
    <head>
    Title
    </head>
    <body>
    """

    def __init__(self, issue, book_properties):
        """
        issue -- Magazine issue object
        book_properties -- BookProperties object
        """
        self.issue = issue
        self.links = []
        self.articles = []
        self.categories = []
        self.fail = False
        for article in issue.article_set.all():
            #if article.category_set.all().count() > 0:
            category = article.category.all()[0]

            found = False
            for cat in self.categories:
                if cat[0] is category:
                    cat[1].append(article)
                    found = True
                    break
            if not found:
                self.categories.append((category, [article]))
            self.articles.append(article)

        self.toc = ""
        self.file = ""
        self.book = Book(book_properties, issue.get_link())
        self.images = []
        self.temp_dir = tempfile.mkdtemp()

    def load_html(self, link):
        print "opening %s" % link
        try:
            opener = urllib.FancyURLopener()
            opener.addheader("Accept-Charset", "windows-1251")

            page = opener.open(link).read()
        except Exception, e:
            print "Error: cannot open link %s" % link
            raise e
        try:
            page = re.sub(r'<!DOCTYPE.*>', '', page)
            charset = chardet.detect(page)
            page = page.decode(charset['encoding'])
            page = re.sub("&#8221;", u"”", page)
            page = re.sub("&#8220;", u"“", page)
            page = re.sub("&#8212;", u"—", page)
            page = re.sub("&#8230;", u"…", page)
            soup = BeautifulSoup(page, fromEncoding=charset['encoding'])
        except Exception, e:
            self.fail = True
            raise e

        noindexes = soup.findAll("noindex")
        for noindex in noindexes:
            noindex.extract()

        scripts = soup.findAll("script")
        for script in scripts:
            script.extract()

        for attr in ["text", "bgcolor", "xlink", "vlink", "link", "leftmargin",
                     "topmargin", "rightmargin", "bottommargin", "marginheight",
                     "marginwidth", "name", "align", "size", "width"]:

            all = soup.findAll(attrs={attr: re.compile(".*")})
            for item in all:
                del item[attr]

        all = soup.findAll(attrs={"href": re.compile("#.*")})
        for item in all:
            del item['href']

        empty_a = soup.findAll(lambda tag: tag.name == "a" and not tag.text)
        for item in empty_a:
            item.extract()

        for img in soup.findAll('img'):
            match = re.search(r"^.*/", link)
            img_name = dict(img.attrs)['src']
            if img_name == "/.img/t.gif":
                img.extract()
                continue
            image = urllib.urlopen("%s%s" % (match.group(0), img_name))
            print "%s%s" % (match.group(0), img_name)
            extension = img_name.split(".")[-1]
            local_img_name = self.temp_dir + "/%d" % (len(self.images) + 1) + "." + extension
            file = open(local_img_name, 'w')
            file.write(image.read())
            file.close()
            self.images.append(local_img_name)

        html = soup.find('html')
        html['xmlns'] = "http://www.w3.org/1999/xhtml"
        self.names = []
        self.titles = []

        file = ""
        file += '<?xml version="1.0" encoding="utf-8"?>\n'
        file += soup.prettify()
        file = re.sub("&nbsp;", "&#160;", file)
        file = re.sub("&(?!amp;|quot;|nbsp;|gt;|lt;|laquo;|raquo;|copy;|reg;|bul;|rsquo;|#160;)", "&amp;", file)

        return file

    def parse(self):

        if self.fail:
            return -1

        for i, article in enumerate(self.articles):
            text = self.load_html(article.link)
            file_name = self.temp_dir + "/%d.html" % i
            file = open(file_name, "w")
            file.write(text)
            file.close()
            art_cat = article.category.all()[0]
            category = Category(art_cat.name, "cat%d" %i, i)
            self.book.add_file(file_name, "c%d" % i, article.title, category=category)

    def __erase_xml_illegal_chars(self, string):
        remove_re = re.compile(u'[^\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', flags=(re.U | re.M))
                           #% extra)
        out = ""
        for match in remove_re.finditer(string):
            out += match.group(0)

        return out


    def create_book(self):
        if self.fail:
            return False

        if not "temp_dir" in dir(self):
            self.temp_dir = tempfile.mkdtemp()

        for i, image in enumerate(self.images):
            self.book.add_file(image, self.temp_dir + '/im%d' % i, title="", in_spine=False)
        self.book.pack()
        return True