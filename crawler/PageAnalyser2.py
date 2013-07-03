# -*- coding: UTF-8 -*-

"""
This module contains classes for page weighting, book link detection, etc.
"""
__author__ = 'pxanych'


from lib.BeautifulSoup import BeautifulSoup
import ContentExtractor
from crawler.globalcrawersettings import keyword_global_object

class PageAnalyser(object):

    def __init__(self, page):
        self._page_soup = BeautifulSoup.BeautifulSoup(page.data)
        self._body_soup = self._page_soup.find('body')
        self._page_info = page.info
        self.page_url = page.url
        self._words = None
        self._weighted_words = None

    def extract_hrefs(self):
        pass

    def get_page_weight(self):
        content_list = ContentExtractor.extract_mapped_content_list(self._body_soup)[0]
        if not self._words:
            self._words = [s for s in content_list if type(s) != int]
            self._weighted_words = map(self._weight_words, self._words)
        return sum(self._weighted_words)


    def weight_links(self, window_width = 1):
        """
        result: [(link, weight)]:
        - link is BeautifulSoup tag (<a>)
        - weight is integer
        """
        content_list, links = ContentExtractor.extract_mapped_content_list(self._body_soup)
        link_count = len(links)
        if not self._words:
            self._words = [s for s in content_list if type(s) != int]
            self._weighted_words = map(self._weight_words, self._words)
        weights = self._weighted_words
        left = 0
        right = window_width
        win_weight = reduce( lambda x,y: x + y, weights[0:min(window_width,link_count)], 0 )
        weighted_links = []
        if link_count <= window_width:
            return map( lambda x: (x, win_weight), links )
        for i in xrange(window_width):
            weighted_links.append( (links[i], win_weight) )
            right += 1
            win_weight += weights[right]
        for i in xrange(window_width, link_count - window_width):
            weighted_links.append( (links[i], win_weight) )
            left += 1
            right += 1
            win_weight += weights[right] - weights[left]
        for i in xrange( link_count - window_width, link_count ):
            weighted_links.append( (links[i], win_weight) )
            left += 1
            win_weight -= weights[left]
        return weighted_links

    def _weight_words(self, words):
        weight = 0
        for word in words.strip().split(' '):
            weight += keyword_global_object.key_words.get(word.lower(), 0)
        return weight