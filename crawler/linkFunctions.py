"""This module contains functions and classes for different
operations on URLs and links."""

#!/usr/bin/python

import types
import urlparse
import re

class LinkAnalyser:

    def __init__( self, link_soup, parent_page_url ):
        self.link_soup = link_soup
        self.parent_page_url = parent_page_url
        self.attributes = {}
        self.url = ''
        self.nofollow = False
        self.relative = False
        return

    def analyse( self, no_query = True, no_fragment = True ):
        for k,v in self.link_soup.attrs:
            self.attributes[k] = v
        href_attr = self.link_soup.get('href')
        if not -1 < href_attr.find('://') < 7:
            self.relative = True
            self.url = URLParser(href_attr).build_url( self.parent_page_url,
                                                       no_query,
                                                       no_fragment )
        return

    
def isHttpLink( link ):
    """
    Checks whether the link is 'http://...' link
    """
    return link[:4] == 'http'

def is_html_url( url ):
    """
    Checks whether the url is html document address
    """
    #tgt = url.split('/')[-1]
    if re.match('http://(www.)?[\w-]*.\w*([\w%-]*/)*((\w+(\.htm(l?))?)|())\Z', url ):
        return True
    return False


class URLParser:

    class URLParserException(Exception):
        pass

    def __init__( self, link ):
        self.parsed_link = urlparse.urlparse(link)

    def build_url( self, parent_url, no_query, no_fragment = True ):
        link_elements = list(self.parsed_link)

        if no_fragment:
            link_elements[5] = ''

        if no_query:
            link_elements[3] = ''
            link_elements[4] = ''

        if self.parsed_link.netloc == '':
            parent_parsed = urlparse.urlparse(parent_url)
            if parent_parsed.scheme and parent_parsed.netloc:
                link_elements[0] = parent_parsed.scheme
                link_elements[1] = parent_parsed.netloc
            else:
                raise URLParser.URLParserException(
                        'No <http://netloc> in link and parent_url' )

        if link_elements[0] != 'http':
            raise  URLParser.URLParserException('Not a <http://...> url')
        return urlparse.urlunparse(link_elements)

    def get_netloc( self ):
        """
        Gets a network location from url.
        E.g. "http://netloc/path/blablabla" -> "http://netloc"
        """
        link_elements = list(self.parsed_link[0:2]) + ['','','','']
        return urlparse.urlunparse(link_elements)


def get_netlock(url):
    return URLParser(url).get_netloc()


def mass_build_lw( parent_url, links ):
    links_list = links.items()
    urls = {}
    for link, weight in links_list:
        if type(link) == types.NoneType:
            continue
        url = URLParser(link).build_url(parent_url, False)
        if url is None:
            continue
        urls[url] = weight
    return urls
            
