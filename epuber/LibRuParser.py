#!/usr/bin/python
#-*- coding: utf-8 -*-

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
from epub import Book, BookProperties
import prettify

from django.core.files.uploadedfile import UploadedFile
import tempfile
try:
    from epuber.local_settings import *
except:
    pass


class LibRuParser:
    """
    Class for converting lib.ru to epub.
    """
    def __init__(self, link, book_properties):
        """
        link -- lib.ru link
        book_properties -- BookProperties object
        """
        self.link = link
        try:
            self.page = urllib.urlopen(link).read()
        except Exception, e:
            print "Error: cannot open link %s" % link
            print e

        self.fail = False
        self.page = prettify.remove_spaces(self.page)
        try:
            charset = chardet.detect(self.page)
            self.soup = BeautifulSoup(self.page, fromEncoding=charset['encoding'])
        except:
            self.fail = True

        self.toc = ""
        self.file = ""
        book_name = link.split("/")[-1].split(".")[0]
        self.book = Book(book_properties, link)
        self.images = []

    def parse(self):
        if self.fail:
            return -1
        html = self.soup.find('html')
        html['xmlns'] = "http://www.w3.org/1999/xhtml"
        table = self.soup.find('table', width='30%')
        self.names = []
        self.titles = []

        form = self.soup.find('form')
        if form:
            form.extract()
        try:
            select = self.soup.find('select')
            select.extract()
        except:
            pass

        if not table:
            self.file += '<?xml version="1.0" encoding="utf-8"?>'
            self.file += self.soup.prettify()
            self.file, n = re.subn("&(?!amp;|quot;|nbsp;|gt;|lt;|laquo;|raquo;|copy;|reg;|bul;|rsquo;|#160;|#187;)", "&amp;", self.file)
            print "Table not found"
            return 

        for a in table.findAll('a'):
            if a['href'][1:]:
                self.names.append('<a name="%s">' % a['href'][1:])
            self.titles.append(a.text)
            #self.toc += a.text + '\n'

        self.toc = "\n".join(self.names)

        table.extract()


        self.temp_dir = tempfile.mkdtemp()
        for img in self.soup.findAll('img'):
            match = re.search(r"^.*/", self.link)
            img_name = dict(img.attrs)['src']
            image = urllib.urlopen("%s%s" % (match.group(0), img_name))
            #print "%s%s" % (match.group(0), img_name)
            file = open(self.temp_dir + "/%s" % img_name, 'w')
            file.write(image.read())
            file.close()
            self.images.append(self.temp_dir + "/%s" % img_name)

        self.file += '<?xml version="1.0" encoding="utf-8"?>'
        self.file += self.soup.prettify()
        self.file = re.sub("&(?!amp;|quot;|nbsp;|gt;|lt;|laquo;|raquo;|copy;|reg;|bul;|rsquo;|#160;|#187;)", "&amp;", self.file)

    HTML_HEADER = """
    <html>
    <head>
    Title
    </head>
    <body>
    """

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
        paragraphs = []
        temp_file = self.file.decode("utf-8")

#        temp_file = self.__erase_xml_illegal_chars(temp_file)

        if not "temp_dir" in dir(self):
            self.temp_dir = tempfile.mkdtemp()
        if not self.names:
            file = open(self.temp_dir + "/0.html", 'w')
            file.write(self.file)
            file.close()
            os.system(EPUBER_DIR + '/remove_illegal.py <' + self.temp_dir + "/0.html >" + self.temp_dir + "/tmp")
            shutil.move(self.temp_dir + "/tmp", self.temp_dir + "/0.html")
            self.book.add_file(self.temp_dir + "/0.html", 'c0', "")
        else:
        
            for i, name in enumerate(self.names):
                split_index = temp_file.find(name)
                if i == 0:
                    paragraph = ""
                else:
                    paragraph = self.HTML_HEADER
                
                paragraph += temp_file[:split_index]
                soup = BeautifulSoup(paragraph)
                paragraph = soup.prettify()
                paragraphs.append(paragraph)
                temp_file = temp_file[split_index:]
                #soup = BeautifulSoup(temp_file)
                #temp_file = soup.prettify()
            paragraphs.append(BeautifulSoup(self.HTML_HEADER + temp_file).prettify())
        for i, paragraph in enumerate(paragraphs):
            file = open(self.temp_dir + "/%d.html" % i, 'w')
            file.write(paragraph)
            file.close()
            os.system(EPUBER_DIR + '/remove_illegal.py <' + self.temp_dir + "/%d.html >" % i + self.temp_dir + "/tmp")
            shutil.move(self.temp_dir + "/tmp", self.temp_dir + "/%d.html" % i)
            self.book.add_file(self.temp_dir + "/%d.html" % i, 'c%d' % i, self.titles[i])
        for i, image in enumerate(self.images):
            self.book.add_file(image, self.temp_dir + '/im%d' % i, title="", in_spine=False)
        self.book.pack()
        return True

class _ExistingFile(UploadedFile):
    ''' Utility class for importing existing files to FileField's. '''

    def __init__(self, path, *args, **kwargs):
        self.path = path
        super(_ExistingFile, self).__init__(*args, **kwargs)

    def temporary_file_path(self):
        return self.path

    def close(self):
        pass

    def __len__(self):
        return 0

def get_book(link):
    http = link + "_with-big-pictures.html"
    http = string.replace(http, "koi/", "")
    name="temp"
    language = "ru"
    authors = {}
    author_name = ""
    genres = []
    temp_name = 'temp.epub'
    properties = BookProperties("books/" + temp_name, name)
    properties.language = language
    properties.author = author_name
    properties.authors = authors
    properties.genre = ", ".join(genres)
    lrp = LibRuParser(http, properties)

    lrp.parse()
    if not lrp.create_book():
        print "Error in creating book."



def main():
    from book.models import Book, Author


    books = Book.objects.all()

    was_last_book = False
    for book in books:
        if EpubBook.objects.filter(book=book):
            continue
        http = book.book_file.get_query_set()[0].link + "_with-big-pictures.html"
        http = string.replace(http, "koi/", "")
        #if not was_last_book and last_book == http + "\n":
        #    was_last_book = True

        #if not was_last_book:
        #    break
        name = book.title
        language = book.language
        authors = {}
        author_name = ""
        genres = []
        for i, author in enumerate(book.author.get_query_set()):
            if i == 0:
                author_name = author.name
            else:
                authors.append(author.name)
        for tag in book.tag.get_query_set():
            genres.append(tag.name)

        temp_name = 'temp'
        properties = BookProperties("books/" + temp_name, name)
        properties.language = language
        properties.author = author_name
        properties.authors = authors
        properties.genre = ", ".join(genres)
        lrp = LibRuParser(http, properties)

        lrp.parse()
        if not lrp.create_book():
            print "Error in creating book."
            continue

        ebook = EpubBook.objects.create()
        ebook.name.save(name + ".epub", _ExistingFile("books/" + temp_name + ".epub"))
        ebook.book = book
        ebook.save()

        last_book = http


    #book = epub.Book(book_name, book_name)#, language=lang, 
                       #subject=subject, description=description, 
                       #genre=type, date=date, rights=rights)
    #book.split_by_toc(lrp.toc, lrp.file)
    #book.pack()

if __name__ == "__main__":
    #get_book("http://lib.ru/koi/MEMUARY/MARGOLIN/Puteshestvie_v_stranu_ze-ka.txt")
    #get_book("http://lib.ru/koi/NEWPROZA/ANCHEWSKAYA/infire.txt")
    get_book("http://lib.ru/koi/MEMUARY/BERIA/sber.txt")
