# -*- coding: utf-8 -*-

import re
from analyser.core.info.BookInfo import BookInfo
from analyser.adds.helpers import make_correct_link

class Retriever:
    "retriever for vseknigi.org"

    @staticmethod
    def get_genres_links(soup):
        big_genres = []
        big_genre_anchors = soup.findAll('a', {'class':'biggenre'} )
        for big_genre_anchor in big_genre_anchors:
            link = big_genre_anchor['href']
            #tag = big_genre_anchor.text
            big_genres.append( link )
        return big_genres

    @staticmethod
    def correct_book_info(book_info,page_link):
        new_links = {}
        for format, link in book_info.links.items():
            new_links[format] = make_correct_link(page_link, link)
        book_info.links = new_links
        book_info.image = make_correct_link(page_link, book_info.image)
        book_info.pagelink = page_link
        return book_info

    @staticmethod
    def get_book_info(soup):
        div = soup.find('div', {'class' : 'book_body'})
        book_info = BookInfo()
        field = Retriever.get_field(div, u'Название:')
        if field:
            match = re.match(u"Название:(.+)", field.text)
            if match and match.groups():
                book_info.title = match.groups(0)[0]
        #author
        field = Retriever.get_field(div, u'Автор:')
        book_info.authors = [ anchor.text for anchor in field.findAll('a')] if field else []
        #summary
        field = Retriever.get_field(div, u'Описание книги:')
        if field and field.p:
            book_info.summary = field.p.text
        #images
        img = soup.find('img', {'class' : 'thumb'})
        book_info.image = img['src'] if img else None
        #tags
        field = Retriever.get_field(div, u'Жанр:')
        if field:
            book_info.tags = [ tag.text for tag in field.findAll('a')]
        #links
        field = Retriever.get_field(div, u'Скачать книгу бесплатно:')
        if field:
            for link_anchor in field.findAll('a'):
                book_info.links [link_anchor.text] = link_anchor['href']
        return book_info

    @staticmethod
    def get_field(soup, name, tag='li'):
        lis = soup.findAll(tag)
        for li in lis:
            if re.match('^%s' % name, li.text):
                return li
        return None

    @staticmethod
    def get_link_pages(soup, page_link):
        link_pages = [ ]
        td = Retriever.get_field(soup, u'Страницы:', 'td')
        if td:
            anchors = td.findAll('a')
            anchors = anchors[:-1]
            link_pages += [ make_correct_link(page_link, anchor['href']) for anchor in anchors ]
        return link_pages

    @staticmethod
    def get_book_links(soup):
        book_links = []
        tds = soup.findAll('td', {'class' : 'head'})
        for td in tds:
            anchor = td.find('a')
            if anchor and anchor.has_key('title'):
                book_links.append( anchor['href'] )
        return book_links
