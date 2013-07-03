import urllib

from lib.BeautifulSoup.BeautifulSoup import BeautifulSoup
from analyser.parsers.OPDS.Retriever import Retriever as OPDS_retriever
"authomatic tests"

def is_acquisition_test():
    print "OPDS_tests: is acquisition test"
    feed = urllib.urlopen('http://www.feedbooks.com/userbooks/top.atom?added=month&lang=ru')
    soup = BeautifulSoup(feed)
    is_acq = OPDS_retriever.is_acquisition_feed(soup)
    assert is_acq == True
    feed = urllib.urlopen('http://www.feedbooks.com/catalog')
    soup = BeautifulSoup(feed)
    is_acq = OPDS_retriever.is_acquisition_feed(soup)
    assert  is_acq == False

def run_tests():
    is_acquisition_test()
