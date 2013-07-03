from server.django.db.models.query_utils import Q

try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

from server.book.models import Book, BookFile, Author , Annotation , Language, Tag
from analyser.core.info.BookInfo import  BookInfo
from analyser.core.db.preprocessing import preprocess_bookinfo
from analyser.adds import logger
from server.django.db.models import Q

class BooksToConsole:
    """
    output info about books to console
    """
    def save_books(self,books):
        for book in books:
            #print book, '\n\n'
            book = preprocess_bookinfo(book)
            print  book.to_string(), '\n\n'


            
class BooksToDatabase:
    """
    saves info about books to database

    responsibility: valid information, transforms if it's necessary (like tags lower)
    """

    def __init__(self):
        #self.myLid = Lid()
        pass

    def save_books(self,books):
        """
        adding info about list of books in database
        """
        for book in books:
            self.save_book(book)

    def save_book(self,book_info):
        book_info = preprocess_bookinfo(book_info)
        book = self.get_exist_book_or_none(book_info)
        import time
        time.sleep(2)
        if book:
            self.update_book(book_info, book)
            action = 'UPDATED'
        else:
            self.create_new_book(book_info)
            action = 'SAVED'

        result = u"%s %s" % ( action, book_info.simple_string() )
        logger.write_success(result)
        print result.encode('utf8')


    def update_book(self,book_info, book):
        " updates existed book"
        if book.pagelink != book_info.pagelink:
            book.pagelink += '; ' + book_info.pagelink
        book.set_lang(book_info.language)
        for name in book_info.authors:
            book.add_author(name)
        for tag_string in book_info.tags:
            book.add_tag_name(tag_string)
        #annotations
        if book_info.summary:
            book.add_annotation(book_info.summary)
        for type, link in book_info.links.items():
            book.add_bookfile(link,type)
        if book_info.image:
            book.image = book_info.image
        book.save()
        

    def create_new_book(self,book_info):
        "  book is not in database yet;     creates new book "
        book = Book(title=book_info.title, pagelink = book_info.pagelink)
        book.set_lang(book_info.language)
        book.save()
        if book_info.summary:
            book.add_annotation(book_info.summary)
        for name in book_info.authors:
            book.add_author(name)
        for tag_string in book_info.tags:
            book.add_tag_name(tag_string)
        for type, link in book_info.links.items():
            book.add_bookfile(link,type)
        book.image = book_info.image
        book.save()


    def get_exist_book_or_none(self,book_info):
        "checks if book exist, return Book or none. Criteries of existing are: same title and same authors"
        #TODO unique checking should be improved: add case not sensitive search
        all_query = Q(title=book_info.title)
        authors_query = None
        for author in book_info.authors:
            author_query = Q(author__name=author)
            authors_query = authors_query | author_query if authors_query else author_query
        all_query = all_query & authors_query if authors_query else all_query
        books = Book.objects.filter(all_query)
        if not books:
            return None
        return books[0]
    
    def is_book_exist(self, book_info):
        """
        DEPRECATED
        checks out, if book is exist in database
         return bool and book ( or None)
        """
        for type, link in book_info.links.items():
            try:
                bookfile = BookFile.objects.get( link_hash = md5(link).hexdigest() )
                books = bookfile.book_set.all()
                if books:
                    return True, books[0]
            except BookFile.DoesNotExist:
                continue
            try:
                book = Book.objects.get(author__name=book_info.authors, title=book_info.title)
                return True, book
            except Book.DoesNotExist:
                continue
        return False, None

def get_bookinfo_from_db(id):
    bookinfo = BookInfo()
    book = Book.objects.get(id=id)
    bookinfo.title = book.title
    bookinfo.authors = [ author.name for author in book.author.all() ]
    bookinfo.pagelink = book.pagelink
    bookinfo.language = book.language.short
    annotations = book.annotation_set.all()
    if annotations:
        bookinfo.summary = annotations[0]
    for bookfile in book.book_file.all():
        bookinfo.links[bookfile.type] = bookfile.link
    bookinfo.tags = [ tag.name for tag in book.tag.all()]
    bookinfo.image = book.image.name if book.image else None
    return bookinfo



