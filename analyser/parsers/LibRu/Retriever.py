# -*- coding: utf-8 -*-

import re
import urlparse
from analyser.core.info.BookInfo import BookInfo
from analyser.core.db.preprocessing import  preprocess_authors
from analyser.adds import helpers
from analyser.adds import logger
from analyser.parsers import get_soup
from analyser.core.tasking.download_managers import WaitingDM
from Preprocessor import Preprocessor
from analyser import settings


class Retriever:

    SITE_LINK = 'http://lib.ru' #TODO this link should be in one place (DRY principle)
    TAGS_MAPPING = {} #lazy initialization
    DIR_REGEX = r'^(\.\./|[A-Za-z])[A-Za-z/-_]+$' #TODO if folder has ../../ level ?
    BOOK_REGEX = r'\.txt$'
    IGNORE_DIRS = settings.LIBRU_IGNORE_DIRS
    IGNORE_BOOKS = settings.LIBRU_IGNORE_BOOKS


    @staticmethod
    def get_accept_dirs(soup, link=''):
       return filter(lambda check: Retriever.filter_accept(check, Retriever.IGNORE_DIRS),
                     Retriever.get_dirs(soup,link))

    @staticmethod
    def get_accept_books(soup,link=''):
       return filter( lambda check: Retriever.filter_accept(check, Retriever.IGNORE_BOOKS),
                      Retriever.get_books(soup,link))


    @staticmethod
    def get_dirs(soup,link=''):
        anchors = soup.findAll('a',href=re.compile(Retriever.DIR_REGEX))
        dirs = {}
        for anchor in anchors:
            href = helpers.make_correct_link(link, anchor['href'])
            if helpers.check_local_link(Retriever.SITE_LINK, href):
                dirs[href] = anchor.text
        return dirs.items()

    @staticmethod
    def get_books(soup,link=''):
        anchors = soup.findAll('a',href=re.compile(Retriever.BOOK_REGEX))
        books = {}
        for anchor in anchors:
            href = helpers.make_correct_link(link, anchor['href'])
            if helpers.check_local_link(Retriever.SITE_LINK, href):
                books[ href] = anchor.text
        return books.items()


    @staticmethod
    def filter_accept(checking, ignore_list):
        link, name = checking
        regexps = [ re.compile(regexp) for regexp in ignore_list]
        for regexp in regexps:
            if regexp.search(link):
                return False
        return True



    @staticmethod
    def get_authors_and_title(text):
        #print text.encode('utf8')
        pattern = u'\x14(.*)\x15'
        m = re.search(pattern, text.split('\n')[0])
        all = m.group(1)
        #print all.encode('utf8')
        authors, title = Preprocessor.extract_authors(all)
        return authors,title

    @staticmethod
    def get_tag_by_link(link):
        url = helpers.get_url_from_link(link).strip('/').split('/')[0]
        if not Retriever.TAGS_MAPPING:
            dm = WaitingDM()
            print 'downloading main page of LibRu for retrieving tags...'
            html = dm.download( helpers.get_site_root_link(link) )
            soup = get_soup(html)
            dirs = Retriever.get_dirs(soup)
            for link, tag in dirs:
                Retriever.TAGS_MAPPING[link.strip('/')] = tag
        if not Retriever.TAGS_MAPPING.has_key(url):
            #TODO make other way for retrieving of tags for this case
            logger.write_fail("LibRu parser: can't find tag in main page",link=link, url=url)
            return None
        return Retriever.TAGS_MAPPING[url]




