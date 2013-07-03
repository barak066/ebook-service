"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client

from book.models import Author
from book.models import Book
from book.models import Language

class OpenTestCase(TestCase):
    def test_opensearch(self):
        """ tests opensearch response"""        
        client = Client()
        response = client.get('/opensearch/')
        print 'status code for open search', response.status_code
        self.failUnlessEqual(response.status_code, 200)
        
#    def test_all_books_xhtml(self):
#        """ tests all books in xhtml"""        
#        client = Client()
#        response = client.get('/all/')
#        print 'status code for all books', response.status_code
#        self.failUnlessEqual(response.status_code, 200)   

#    def test_all_books_opds(self):
#        """ tests all books in opds"""    
#        client = Client()
#        response = client.get('/all.atom/')
#        print 'status code for all books in opds', response.status_code
#        self.failUnlessEqual(response.status_code, 200)         

    def test_catalog_xhtml(self):
        """ tests catalog response in xhtml"""
        client = Client()
        response = client.get('/catalog/')
        print 'status code for catalog', response.status_code
        self.failUnlessEqual(response.status_code, 200)    
        
    def test_catalog_opds(self):
        """ tests catalog response in opds"""
        client = Client()
        response = client.get('/catalog.atom/')
        print 'status code for catalog in opds', response.status_code
        self.failUnlessEqual(response.status_code, 200)   
        
    def test_author(self):
        """ tests author response"""
        client = Client()
        author = Author(name="Author")
        author.save()
        author_id = author.id

        response = client.get('/author.atom/id%s/' %(author_id,))
        print 'status code for good author request in atom', response.status_code
        self.failUnlessEqual(response.status_code, 200)
        
        response = client.get('/author/id%s/' %(author_id,))
        print 'status code for good author request in xhtml', response.status_code
        self.failUnlessEqual(response.status_code, 200)

        response = client.get('/author.atom/id%s/' %(author_id + 1,))
        print 'status code for bad author request in atom', response.status_code
        self.failUnlessEqual(response.status_code, 404)                          

        response = client.get('/author/id%s/' %(author_id + 1,))
        print 'status code for bad author request in xhtml', response.status_code
        self.failUnlessEqual(response.status_code, 404)                          

    def test_book(self):
        """ tests book response"""
        client = Client()
        lang = Language(id=0)
        lang.save()
        book = Book(title="Book", language=lang)
        book.save()
        book_id = book.id
        
        response = client.get('/book.atom/id%s/' %(book_id,))
        print 'status code for good book request in atom', response.status_code
        self.failUnlessEqual(response.status_code, 200)

        response = client.get('/book/id%s/' %(book_id,))
        print 'status code for good book request in xhtml', response.status_code
        self.failUnlessEqual(response.status_code, 200)

        response = client.get('/book.atom/id%s/' %(book_id + 1,))
        print 'status code for bad book request in atom', response.status_code
        self.failUnlessEqual(response.status_code, 404)                          
        
        response = client.get('/book/id%s/' %(book_id + 1,))
        print 'status code for bad book request in xhtml', response.status_code
        self.failUnlessEqual(response.status_code, 404)                   
        
    def test_search(self):
        """ tests search response"""
        client = Client()
        lang = Language(id=0)
        lang.save()
        book = Book(title="Book", language=lang)
        book.save()
        
        response = client.get('/search?query=Book')        
        print 'status code for good search request', response.status_code
        self.failUnlessEqual(response.status_code, 200)
        
        response = client.get('/search.atom?query=Book')        
        print 'status code for good search request', response.status_code
        self.failUnlessEqual(response.status_code, 200)
        
    def test_discover(self):
        """ tests links from catalog"""
        client = Client()
        response = client.get('/discover/authors')
        print 'status code for authors', response.status_code
        self.failUnlessEqual(response.status_code, 200)

        response = client.get('/simple_search')        
        print 'status code for simple search', response.status_code
        self.failUnlessEqual(response.status_code, 200)

        response = client.get('/extended_search')        
        print 'status code for extended search', response.status_code
        self.failUnlessEqual(response.status_code, 200)
        
        response = client.get('/discover/languages')        
        print 'status code for languages', response.status_code
        self.failUnlessEqual(response.status_code, 200)        
        
        response = client.get('/discover/subjects')        
        print 'status code for tags', response.status_code
        self.failUnlessEqual(response.status_code, 200)        
        
