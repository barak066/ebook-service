#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
from Uniqify import uniqify_nop
import threading

class UrlParser:

    #finished = False
    removeSelfLinks = 3 # 0 - do not remove
                        # 1 - remove links only
                        # 2 - remove domains only
                        # 3 - remove both
    urls = []
    domains = []
    pageUrl = ''
    htmlCode = ''
    domainName = ''
    parseComplete = False

    def __init__( self, pageUrl, htmlCode, domainName, removeSelfLinks = 3 ):
        self.pageUrl = pageUrl
        self.htmlCode = htmlCode
        self.domainName = domainName
        self.removeSelfLinks = removeSelfLinks

    
    def parseUrls( self ):
       
        soup = BeautifulSoup( self.htmlCode )
        a_tags = soup.findAll('a')
        
        links = []
        for tag in a_tags:
            for name, value in tag.attrs:
                if name == 'href':
                    links.append(value)
                    
        urls = filter( (lambda str: str.find('http://') == 0), links )
                
        relLinks = filter( (lambda str: str.find('http://') == -1), links )
        relLinks = filter( (lambda str: str != '/'), relLinks )
        relLinks = [ self.domainName + relLink for relLink in relLinks ]

        urls += relLinks
        
        urls = uniqify_nop(urls)

        if self.removeSelfLinks & 1:
            if urls.count( self.pageUrl ) != 0:
                urls.remove( self.pageUrl )        

        self.urls = urls
        return

    def parseDomains( self ):
        if self.urls.__len__() == 0:
            self.parseUrls()
            
        domains = []
        noHttpUrls = [ url[7:] for url in self.urls]

        for url in noHttpUrls:
            index = url.find('/')
            domains.append( url[:index != -1 and index or None] )
        
        selfDomain = self.pageUrl[7:]
        index = selfDomain.find('/')
        if index != -1:
            selfDomain = self.pageUrl[:index]

        domains = uniqify_nop(domains)

        if self.removeSelfLinks & 2:
            if domains.count( selfDomain ) != 0:
                domains.remove( selfDomain )

        self.domains = domains
        self.parseComplete = True
        return

    def startParseThread( self ):
        t = threading.Thread( target = self.parseDomains )
        t.start()
        

