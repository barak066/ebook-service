#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
Module for creating epub books.
"""

import zipfile, tempfile
import os
import shutil
import re
from django import template
from django.template.loader import get_template
from lib import chardet

class BookProperties:
    """
    Properties of e-book.
    """
    def __init__(self, name = "", title = ""):
        self.name = name
        self.title = title
        self.language = "en"
        self.author = ""
        self.authors = {}
        self.identifier = 0
        self.description = ""
        self.subject = ""
        self.genre = ""
        self.date = ""
        self.rights = ""

class TocTreeNode:
    """
    Node of tree of contents
    """

    def __init__(self, depth):
        self.depth = depth
        self.max_depth = depth
        self.children = []
        self.parent = None

    def append_child(self, node):
        node.depth = self.depth + 1
        node.parent = self
        par = self
        while par:
            par.max_depth = max(par.max_depth, node.depth)
            par = par.parent

        self.children.append(node)

class Category:
    """
    Category of magazines
    """
    def __init__(self, title, file_name, i):
        self.title = title
        self.file_name = file_name
        self.i = i
        self.files = []

    def add_file(self, file):
        self.files.append(file)

    def __eq__(self, other):
        return self.title == other.title

    def pretty_name(self):
        return self.file_name.split("/")[-1]

class File:
    """
    File for table of contents
    """
    def __init__(self, file_name, title, i, id, in_spine=True, is_linear=True, media_type="", category=None):
        self.file_name = file_name
        self.title = title
        self.i = i
        self.in_spine = in_spine
        self.is_linear = is_linear
        self.identificator = id
        self.media_type = media_type
        self.category = category

    def pretty_name(self):
        return self.file_name.split("/")[-1]

    def __str__(self):
        return "File" + self.title

class Book:
    """
    Class of electronic book.
    """
    def __init__(self, properties, link="", categories=None):
        """
        name -- file name
        author -- {name : role}
        properties -- BookProperties object
        """
        self.name = properties.name
        self.title = properties.title
        self.language = properties.language
        self.description = properties.description
        self.subject = properties.subject
        self.genre = properties.genre
        self.date = properties.date
        self.rights = properties.rights

        self.identifier = properties.identifier
        self.author = properties.author
        self.authors = properties.authors
        self.files = []
        self.files_count = 0

        self.categories = []

        self.tempdir = tempfile.mkdtemp()

        start_template = get_template("epuber-templates/start-page.html")
        site_link = ""
        if len(link.split("/")) >= 2:
            site_link = "http://" + link.split("/")[2] + "/"
        start_context = template.Context(
                {'link': link,
                 "site_link": site_link})
        start_page = open(self.tempdir + "/start-page.html", 'w')
        start_page.write(start_template.render(start_context).encode("utf-8"))
        start_page.close()
        self.add_file(self.tempdir + "/start-page.html", "st0", "Start page")

    def add_file(self, file_name, identificator, title, in_spine=True, 
                 is_linear=True, category=None):
        """
        Add file into book.
        """
        self.files_count += 1
        if category:

            file = File(file_name, title, self.files_count + 1, identificator, in_spine, is_linear, category)
            self.files.append(file)
            if category not in self.categories:
                self.categories.append(category)
            category.add_file(file)
            category.i = self.files_count
        else:
            self.files.append(File(file_name, title, self.files_count, identificator, in_spine, is_linear))
            
    def __create_mime(self, tempdir, zip_file):
        """
        Creates mimetype file and packs it into "file".
        """
        mimetype = open(tempdir + '/' + "mimetype", 'w')
        mimetype.write("application/epub+zip")
        mimetype.close()

        zip_file.write(tempdir + "/mimetype", arcname="/mimetype", compress_type=zipfile.ZIP_STORED)
        os.remove(tempdir + '/' + "mimetype")

    def __create_meta_inf(self, tempdir, zip_file):
        """
        Creates META-INF directory and packs it into "file".
        """
        os.mkdir(tempdir + '/' + "META-INF")

        container = open(tempdir + "/META-INF/container.xml", 'w')
        container_template = get_template("epuber-templates/container.xml")
        container.write(container_template.render(template.Context({})))
        container.close()

        zip_file.write(tempdir + "/META-INF/container.xml", arcname="/META-INF/container.xml")
        os.remove(tempdir + "/META-INF/container.xml")

    def __create_content(self, tempdir, zip_file):
        """
        Creates content file in the /OEBPS directory and packs it into "file".
        """
        files = []
        for file in self.files:
            file_name = file.file_name

            name = file_name.split("/")[-1]
            shutil.copyfile(file_name, tempdir + "/OEBPS/" + name)

            zip_file.write(tempdir + "/OEBPS/" + name, arcname="/OEBPS/" + name)

            os.remove(tempdir + "/OEBPS/" + name)

            if name.split(".")[-1] in ["jpeg", "jpe", "jpg"]:
                media_type = "image/jpeg"
            elif name.split(".")[-1] in ["gif"]:
                media_type = "image/gif"
            elif name.split(".")[-1] in ["png"]:
                media_type = "image/png"
            else:
                media_type = "application/xhtml+xml"

            files.append({"identificator": file.identificator, "name": name, "media_type": media_type})

        content_template = get_template("epuber-templates/content.opf")
        
        content_context = template.Context({'self': self, 'files': files, 'self_files': self.files})

        content = open(tempdir + "/OEBPS/content.opf", 'w')
        content.write(content_template.render(content_context).encode("utf-8"))
        content.close()

        zip_file.write(tempdir + "/OEBPS/content.opf", arcname="/OEBPS/content.opf")
        os.remove(tempdir + "/OEBPS/content.opf")

    def __create_toc(self, tempdir, zip_file):
        """
        Creates toc file in the /OEBPS directory.
        """

        toc_template = get_template("epuber-templates/toc.ncx")
        if self.categories:
            toc_context = template.Context({'self': self, 'categories': self.categories})
        else:
            toc_context = template.Context({'self': self, 'files': self.files})

        toc = open(tempdir + "/OEBPS/toc.ncx", 'w')
        toc.write(toc_template.render(toc_context).encode("utf-8"))
        toc.close()

        zip_file.write(tempdir + "/OEBPS/toc.ncx", arcname="/OEBPS/toc.ncx")
        os.remove(tempdir + "/OEBPS/toc.ncx")

    def __create_oebps(self, tempdir, zip_file):
        """
        Creates OEBPS directory and packs it into "file".
        """
        os.mkdir(tempdir + '/' + "OEBPS")

        self.__create_content(tempdir, zip_file)

        self.__create_toc(tempdir, zip_file)

        zip_file.write(tempdir + '/' + "META-INF", arcname="/META-INF")
        zip_file.write(tempdir + '/' + "OEBPS", arcname="/OEBPS")

        os.removedirs(tempdir + '/' + "META-INF")
        os.removedirs(tempdir + '/' + "OEBPS")

    def pack(self):
        """
        Pack book into epub format.
        """
        tempdir = self.tempdir
        shutil.rmtree(tempdir + '/' + "OEBPS", True)
        shutil.rmtree(tempdir + '/' + "META-INF", True)

        zip_file = zipfile.ZipFile(self.name, 'w')

        self.__create_mime(tempdir, zip_file)

        self.__create_meta_inf(tempdir, zip_file)

        self.__create_oebps(tempdir, zip_file)

        zip_file.close()

        for m_file in self.files:
            try:
                os.remove(m_file.file_name)
            except:
                print "Error"

    def txt_to_html(self, input_txt, output):
        """
        Convert txt string to file with name "output".
        """
        charset = chardet.detect(input_txt)
        temp = input_txt.decode(charset['encoding'])
        #temp = temp.replace('&', '&amp;')
        #temp = temp.replace('<', '&lt;')
        #temp = temp.replace('>', '&gt;')
        #temp = temp.replace('"', '&quot;')
        #temp = temp.replace("'", '&#187;')

        paragraphs = temp.split('\n')
        html_template = get_template("epuber-templates/html-template.xhtml")
        html_context = template.Context({'paragraphs': paragraphs})
        
        output_file = open(output, 'w')
        output_file.write(html_template.render(html_context).encode("utf-8"))
        output_file.close()

    def split_by_toc(self, toc, input_str):
        """
        Splits string 'input_str' by table toc.
        """
        toc_list = toc.split("\n")

        temp = input_str
        chapter = ""
        if toc_list[-1] == '':
            del toc_list[-1]
        for i in xrange(len(toc_list)):
            if i < len(toc_list) - 1:
                index = temp.find('\n' + toc_list[i + 1].strip() + '\n')
            else:
                index = -1
            chapter = temp[:index]
            temp = temp[index:]
            file_name = 'chapter%d.xhtml' % (i + 1)
            self.txt_to_html(chapter, file_name)
            self.add_file(file_name, "c%d" % (i + 1), toc_list[i])

    def find_paragraphs(self, input_str):
        """
        Finds paragraps in 'input_str'
        """
        paragraphs = re.split('\n\n.*?\n\n', input_str)
        captions = re.findall('\n\n.*?\n\n', input_str)
        if len(paragraphs) != len(captions): # The case if first caption not found
            captions.insert(0, '')
        paragraphs = [x + y for (x, y) in zip(*(captions, paragraphs))] 
        for i, paragraph in enumerate(paragraphs):
            file_name = 'chapter%d.xhtml' % (i + 1)
            self.txt_to_html(paragraph, file_name)
            self.add_file(file_name, "c%d" % (i + 1), captions[i])

def main():
    """
    Main function.
    """
    book = Book("mybook", "My first epub")
    book_file = open("/home/dima/workspace/ebook-service/epuber/gesse.txt")
    toc_file = open("/home/dima/workspace/ebook-service/epuber/toc.txt")
#    book.split_by_toc(toc_file.read(), book_file.read())
    book.find_paragraphs(book_file.read())
    book_file.close()
    toc_file.close()
    book.pack()

if __name__ == "__main__":
    main()
