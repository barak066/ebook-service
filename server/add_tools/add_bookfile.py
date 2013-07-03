from django.core.management import setup_environ
import settings
setup_environ(settings)

from book.models import Author, Book, Language, Annotation, Tag, BookFile
from spec.external.BeautifulSoup import BeautifulSoup as bs

import sys

def add_bookfile(file_name):
    file_handle = open(file_name, "r")
    content = file_handle.read()
    file_handle.close()
    beaut_soup = bs.BeautifulSoup(content)
    messages = beaut_soup.findAll('message')
    for message in messages:
        type = message.find('mimetype').getText()
        link = message.find('link')
        src = link.get('src')
        try:
            if type == 'epub':
                book_file = BookFile(link=src, type='epub')              
                book_file.save()
            elif type == 'fb2' or type == 'zip':
                book_file = BookFile(link=src, type='fb2')
                book_file.save()
        except:    
            pass        # book_file already in our data base

add_bookfile(sys.argv[1])

            

