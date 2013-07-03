# -*- coding: utf-8 -*-

import re
from analyser.core.info.BookInfo import BookInfo
from analyser.adds.helpers import make_correct_link

class Retriever:

    @staticmethod
    def get_queue(soup):
        queue = []
        ul_categories = soup.find('ul')
        for li_categories in ul_categories.findAll('li', {}, False):
            tag1 =  li_categories.a.text
            for li_sub_categories in li_categories.ul.findAll('li', {}, False):
                tag2 =  li_sub_categories.a.text
                for li_detail in li_sub_categories.ul.findAll('li', {}, False):
                    record = {'tags' : [tag1,tag2], 'link' : li_detail.a['href'] }
                    queue.append(record)
        return queue

    @staticmethod
    def correct_queue(queue, page_link):
        for q in queue:
            q['link'] = make_correct_link(page_link, q['link'])

    @staticmethod
    def get_book_info(soup):
        book_info = BookInfo()
        book_info.title = Retriever.get_field(soup, u'Название:')
        authors = Retriever.get_field(soup, u'Автор\(ы\):')
        if authors:
            book_info.authors = [ authors ]
        book_info.summary = Retriever.get_field(soup, u'Описание:')
        book_info.language = Retriever.get_field(soup, u'Язык:')
        format = Retriever.get_field(soup, u'Формат:')
        link = Retriever.get_field(soup, u'Ссылка 1:', False).a['href']
        book_info.links = {format : link}
        return book_info

    @staticmethod
    def get_field(soup, name, text=True):
        for tr in soup.findAll('tr'):
            if re.match('^%s' % name, tr.text):
                tr2 = tr.findAll('td')[1]
                if text:
                    return tr2.text
                return tr2
        return None




