"""
set and keep internet session alive
need to be used for sites that asks for authorization
"""
import urllib
import urllib2

from urllib2 import ProxyHandler, HTTPHandler, HTTPRedirectHandler, HTTPSHandler, HTTPCookieProcessor

class OpenerHolder:
    user_agent = 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'

    def __init__(self, auth_info, site_link):
        self.http = HTTPHandler()
        self.redirect = HTTPRedirectHandler()
        self.https = HTTPSHandler()
        self.cookie = HTTPCookieProcessor()
        self.auth_info = auth_info
        self.site_link = site_link
        self.authorized = False
        self.opener = urllib2.build_opener(self.redirect, self.http, self.https, self.cookie)

    def authorize(self):
        urllib2.install_opener(self.opener)
        if self.auth_info:
            data = urllib.urlencode(self.auth_info)
            self.opener.open(self.site_link, data )
        else:
            self.opener.open(self.site_link)
        self.authorized = True
        pass

    def urlopen(self, url):
        if not self.authorized:
            self.authorize()
        urllib2.install_opener(self.opener)
        return urllib2.urlopen(url)