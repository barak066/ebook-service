# -*- coding: utf-8 -*-

import urllib

from lib.BeautifulSoup.BeautifulSoup import BeautifulSoup

from analyser.core.db.booksaver import BooksToDatabase

class Parser:
    "Base Parser class"
    def __init__(self):
        self.book_saver = BooksToDatabase() #BooksToConsole()
        #self.state = State()
        pass

    def save_books(self,books):
        self.book_saver.save_books(books)
        pass

    def get_state_filename(self):
        return self.get_filename()

    def get_filename(self):
        "defines in child classes.   returns the name of file, using for debug file and state file"
        pass
    def run_it(self):
        "runs parser"
        pass

    def get_soup(self,page_link):
        "loads page throught the BeautifulSoup, also uses  1 second pause between"
        html = urllib.urlopen( page_link )
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES )
        return soup

