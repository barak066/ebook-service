# -*- coding: utf-8 -*-
from analyser.parsers.LibRu.Retriever import Retriever
from analyser.parsers.LibRu.Preprocessor import Preprocessor
from analyser.parsers import download_soup
from lib.chardet.universaldetector import UniversalDetector

def cleanup_kilobytes_test():
    assert u"Book  yeah!" == Preprocessor.cleanup_kilobytes(u"Book (19 k) yeah!")
    pass

def cleanup_year_test():
    assert u"Book  yeah!" == Preprocessor.cleanup_year(u"Book (1990) yeah!")
    assert u"Book  yeah!" == Preprocessor.cleanup_year(u"Book [1990] yeah!")

def get_authors_test():
    pass

def is_author_test():
    assert Preprocessor.is_author(u"Старый Хелом") == True
    pass
def extract_authors_test():
    authors, title = Preprocessor.extract_authors(u"Старый Хелом")
    assert not authors
    authors, title = Preprocessor.extract_authors(u"О Шекспире")
    assert not authors
    authors, title = Preprocessor.extract_authors(u"Кристофер Сташефф, Уильям Р.Форстчен. Расплата")
    #print authors,title
    pass

def cleanup_numeration_test():
    titles = ['1. Василий Теркин', '2. Теркин на том свете', '62. Модель для сборки', '35.Проклятие вождя','Причесывая Жирафу.. Глава 1.']
    r_titles = ['Василий Теркин', 'Теркин на том свете', 'Модель для сборки', 'Проклятие вождя','Причесывая Жирафу.. Глава 1.']
    for title, r_title in zip(titles, r_titles):
        title = Preprocessor.cleanup_numeration(title)
        assert title == r_title

def get_dirs_test():
    soup = download_soup('http://lib.ru/')
    all_tags = Retriever.get_accept_dirs(soup)
    for link,tag in all_tags:
        print link,tag.encode('utf8')
#    print
    keys = [tag[0] for tag in all_tags]
    keys.sort()
    #print len(keys)
    assert len(keys) == 64
#    for tag in keys:
#        print tag

def get_books_test():
    link = 'http://lib.ru/STRUGACKIE/'
    soup = download_soup(link)
    all_tags = Retriever.get_accept_books(soup,link)
#    for link, tag in all_tags:
#        print link, tag.encode('utf8')
        #print "'%s' -- %s" % ( link, '1')#tag.decode('utf8') )
    assert len(all_tags) == 99
    pass

def get_authors_title_test():
    import urllib
    l = 'http://lib.ru/TXT/ruscience.txt'
    page = urllib.urlopen(l+'_Ascii.txt')
    text = page.read(2048)
    ud = UniversalDetector()
    ud.feed(text)
    ud.close()
    encoding = ud.result['encoding']
    text = unicode(text, encoding)
    authors, title = Retriever.get_authors_and_title(text)
    assert len(authors) == 1
    assert authors[0] == u'Дмитрий Толмацкий'
    assert title == u'Российская наука на пути из реанимации в морг'
#    print 'authors', ",".join( [author.encode('utf8') for author in authors ] )
#    print 'title',title
    pass
        
        
def run_tests():
    print 'libru_tests'
    cleanup_kilobytes_test()
    cleanup_year_test()
    is_author_test()
    extract_authors_test()
    cleanup_numeration_test()
    get_dirs_test()
    get_books_test()
    get_authors_title_test()