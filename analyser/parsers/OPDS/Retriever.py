# -*- coding: utf-8 -*-

import re
from analyser.core.info.BookInfo import BookInfo

class Retriever:
    known_formats = ['epub+zip', 'fb2+zip']
    prohibited_urls = ( r'^https:',
                        r'http://data.fbreader.org/catalogs/litres/my.php',
                        r'http://manybooks.net/opds/new_titles.php'
                        r'http://www.smashwords.com/atom/books/1/newest/epub/any/0'
                        r'http://www.smashwords.com/atom/books/1/popular/epub/any/0'
                        r'https://www.feedbooks.com/user/profile.atom',
                        r'http://www.smashwords.com/atom/publish',
                        r'http://81.1.213.130:8091/opds/polka'
                      )

    @staticmethod
    def get_bookinfo(entry):
        book_info = BookInfo()
        book_info.title = entry.title.text
        book_info.authors = [entry.author.findChild().text]
        #language
        language = entry.find('dc:language') or entry.find('dcterms:language')
        book_info.language = language.text if language else '?'
        #links
        for format in Retriever.known_formats:
            link_to_book_tag = entry.find('link', type="application/"+format)
            if link_to_book_tag:
                book_info.links[format] = link_to_book_tag['href']
        if not book_info.links:
            return None
        #summary
        summary = entry.find('content') or entry.find('summary')
        book_info.summary = summary.text if summary else None
        #tags
        categories = entry.findAll('category')
        if categories:
            for category in categories:
                label = None
                if category.has_key('label'):
                    label = category['label']
                elif category.has_key('term'):
                     label = category['term']
                if label:
                    book_info.tags.append( label )
        return book_info

    @staticmethod
    def is_acquisition_feed(soup):
          """
          checks out if feed is a Acquisition Feed
          returns true if at least one link with rel='http://opds-spec.org/acquisition' exist
          otherwise, returns false
          """
          links = soup.findAll('link', rel=re.compile(r"http://opds-spec\.org/acquisition"))
          if not links:   #TODO clear this hack! (no right relation at link)  at http://www.stanza.epubbooks.ru/stanza/index.xml
              links = soup.findAll('link', type=re.compile("application/[A-z\-0-9]+\+zip"))
          return len(links) > 0

    @staticmethod
    def is_permitted_link(link):
        for pattern in Retriever.prohibited_urls:
            if re.match(pattern, link):
                return False
        return True

    @staticmethod
    def get_entries(soup):
        return soup.findAll('entry')

    @staticmethod
    def get_catalog_link(entry):
        link = entry.find('link', type=re.compile(r"application/atom\+xml") )
        result = link['href'] if link else None
        return result