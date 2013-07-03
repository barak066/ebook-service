from django.core.management import setup_environ
import settings
setup_environ(settings)

from book.models import Author, Book, Language, Annotation, Tag, BookFile
from tools import smart_split
from spec.external.BeautifulSoup import BeautifulSoup as bs
import urllib2
import zipfile
import os

def read_epub(book_file):
    ''' extract information about book title/author from epub '''
    digits = "0123456789"

    link = book_file.link

    try:
        webFile = urllib2.urlopen(link)
    except:
        return
    filename = "downloads/" + link.split('/')[-1]
    localFile = open(filename, 'w')
    localFile.write(webFile.read())
    webFile.close()
    localFile.close()

    file = zipfile.ZipFile(filename, "r")

    data = None
    for i in file.namelist():
        if i.endswith('opf'):
            data = file.read(i)
    file.close()

    beaut_soup = bs.BeautifulSoup(data)
    author_tag = beaut_soup.find('dc:creator')
    if author_tag:
        author_string = author_tag.getText().lower()
    else:
        os.remove(filename)
        return
    if not author_string:
        os.remove(filename)
        return

    ind = author_string.find(" trans by ")    
    if ind != -1:
        author_string = author_string[:ind]
    ind = author_string.find(" translated ")    
    if ind != -1:
        author_string = author_string[:ind]
    ind = author_string.find(" adapted ")    
    if ind != -1:
        author_string = author_string[:ind]
    ind = author_string.find(" by ")
    if ind != -1:
        author_string = author_string[:ind]


    for c in digits:
        author_string = author_string.replace(c, '')

    author_string = author_string.title().strip()

    title_string = beaut_soup.find('dc:title').getText()

    if not title_string:
        os.remove(filename)
        return

    ind = title_string.find(" trans by ")
    if ind != -1:
        title_string = title_string[:ind]
    ind = title_string.find(" translated ")    
    if ind != -1:
        title_string = title_string[:ind]
    ind = title_string.find(" adapted ")    
    if ind != -1:
        title_string = title_string[:ind]
    ind = title_string.find(" by ")
    if ind != -1:
        title_string = title_string[:ind]

    lang_tag = beaut_soup.find('dc:language')
    if lang_tag:
        lang_string = lang_tag.getText()   

        if lang_string:
            try:
                language = Language.objects.get(short=lang_string)         #TODO language
            except:
                try:
                    language = Language.objects.get(short=lang_string[0:2])         #TODO language
                except:
                    language = Language.objects.get(short="?")           
        else:
            language = Language.objects.get(short="?") 
    else:
        language = Language.objects.get(short="?") 

    author = Author.objects.get_or_create(name=author_string)[0]

    book = author.book_set.filter(title=title_string.strip())

    if book:
        book[0].book_file.add(book_file)
    else:    
        book = Book(title=title_string, language=language)
        book.save()
        book.book_file.add(book_file)

        book.author.add(author)

    print 'Added book:  ', "Title: ", title_string, " Author: ", author_string

    description_tag = beaut_soup.find('dc:description')
    if description_tag:
        description_string = description_tag.getText()
        if description_string:
            ann = Annotation.objects.get_or_create(name=description_string.strip(), book=book)        

    tag_tag = beaut_soup.find('dc:subject')
    if tag_tag:
        tag_string = tag_tag.getText()
        if tag_string:
            for c in digits:
                tag_string = tag_string.replace(c, '')
            tags = smart_split([tag_string], [',', '/', '_', '--'])
            for tag_name in tags:
                if len(tag_name) > 25:
                    continue

                tag = Tag.objects.get_or_create(name=tag_name.title().strip())        
                book.tag.add(tag[0])
    os.remove(filename)


for book_file in BookFile.objects.filter(book__isnull=True, type="epub"):
    read_epub(book_file)
