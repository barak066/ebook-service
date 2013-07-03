import os, sys
if not '..' in sys.path:
    sys.path.append('..')
if not '../server' in sys.path:
    sys.path.append('../server')
#os.environ['django_settings_module'] = 'server.settings'
#os.environ['pwd'] = '../server'
from django.core.management import setup_environ
from server import settings

setup_environ(settings)

import re, string
from epuber.epub import Book, BookProperties
from epuber import prettify
try:
    from epuber.local_settings import *
except:
    pass
from lib.BeautifulSoup.BeautifulSoup import *
import tempfile

class DocParser:
    def __init__(self, name, book_properties):
        self.name = name
        self.book = Book(book_properties)

    HTML_HEADER = """
    <html>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <head>
    Title
    </head>
    <body>
    """
    def parse(self, output=""):
        self.temp_dir = tempfile.mkdtemp()
        if output == "":
            output = self.temp_dir + "/tmp.html"

        os.system(PATH_TO_WV_WARE  + 'wvWare -x' + 
                  PATH_TO_WV_HTML + '/wvHtml.xml --charset=cp1251 %s > %s' % 
                  (self.name, output))
        
        paragraphs = []
        #temp_file = self.file.decode("utf-8")
        file = open(self.temp_dir + "/tmp.html", 'r')
        temp_file = prettify.remove_spaces(file.read())
        temp_file = prettify.remove_unnecessary_tags(temp_file)
        soup = BeautifulSoup(temp_file)
        temp_names = soup.findAll(align="center")
        names = []
        titles = []
        for temp_name in temp_names:
            if not re.match(r"^(<.*?>|\s+)*$", str(temp_name)):
                names.append(re.sub(r'\s+', ' ', str(temp_name)))
                temp = re.sub(r"(<.*>|\s+)", " ", temp_name.prettify())
                titles.append(re.sub(r'\s+', " ", temp))

        temp_file = re.sub(r'\s+', ' ', temp_file.decode('cp1251').encode('utf-8'))
        out = open(self.temp_dir + '/tmp', 'w')
        out.write(temp_file)
        out.write("   \n\n\n")
        for name in names:
            out.write(name + "\n\n\n")
        out.close()
            
        if not names:
            print "not names"
            file = open(self.temp_dir + "/0.html", 'w')
            file.write(temp_file)
            file.close()
            self.book.add_file(self.temp_dir + "/0.html", 'c0', "")
        for i, name in enumerate(names):
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
        for i, paragraph in enumerate(paragraphs):
            file = open(self.temp_dir + "/%d.html" % i, 'w')
            file.write(paragraph)
            file.close()
            self.book.add_file(self.temp_dir + "/%d.html" % i, 'c%d' % i, titles[i])
        #for i, image in enumerate(self.images):
        #    self.book.add_file(image, 'im%d' % i, title="", in_spine=False)

        self.book.pack()
        return True

if __name__ == "__main__":
    temp_name = 'temp'
    properties = BookProperties("books/" + temp_name, "test")
    #properties.language = language
    #properties.author = author_name
    #properties.authors = authors
    #properties.genre = ", ".join(genres)
    d = DocParser("/home/dima/Documents/test.doc", properties)
    d.parse()
