# -*- coding: utf-8 -*-

import re
from analyser.core.info.BookInfo import BookInfo
from analyser.adds.helpers import make_correct_link

class Retriever:

    @staticmethod
    def get_pages_number(soup):
        bolds = soup.findAll('b', text=re.compile(u'Страниц'))
        m = re.search('([0-9]+)', bolds[0])
        number = m.group()
        return int(number)

    @staticmethod
    def generate_all_pagelinks_for_genre(link, number):
        pagelinks = []
        for n in xrange(1,number+1):
            pagelink = re.sub('-([0-9]+)','-%d' % n,link)
            pagelinks.append(pagelink)
        return pagelinks

    @staticmethod
    def get_genres(soup):
        hrefs = soup.findAll('a', href=re.compile(r'^/janr/index_janr_[0-9]+'))
        genres = []
        for href in hrefs:
            genre_name = href.text
            genre_link = href['href']
            genre = {'name' : genre_name, 'link' : genre_link}
            genres.append(genre)
        return genres

    @staticmethod
    def get_bookinfos(soup):
        dls = soup.findAll('dl')
        bookinfos = []
        for dl in dls:
            bookinfo = Retriever.get_bookinfo_from_tag_dl(dl)
            bookinfos.append(bookinfo)
        return bookinfos

    @staticmethod
    def postprocess_bookinfo(bookinfo, pagelink, tag):
        bookinfo.pagelink = pagelink
        for format, link in bookinfo.links.items():
            bookinfo.links[format] = make_correct_link(pagelink, link)
        bookinfo.tags.append(tag)
        return bookinfo

    @staticmethod
    def get_bookinfo_from_tag_dl(dl):
        bookinfo = BookInfo()
        anchors = dl.dt.li.findAll('a')
        author_anchor = anchors[0]
        title_anchor = anchors[1]
        bookinfo.links['shtml'] = title_anchor['href']
        bookinfo.authors = [author_anchor.text]
        bookinfo.title = title_anchor.text
        bookinfo.language = 'ru'
        dd = dl.findAll('dd')
        if dd:
            bookinfo.summary = dd[0].text
        return bookinfo




