"Insert action handler for analyzer interface"

try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5
import logging

from django.db.models import Q
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from book.models import Book, Author, AuthorAlias, BookFile, Annotation, Language
from spec.exception import InputDataServerException
from spec.utils import get_language

analyzer_log = logging.getLogger("analyser_logger")
MAIN_LOG = logging.getLogger("main_logger")

def strip_str(tstr):
    '''Removes leading, endig space from string,
    Returns empty string, if str is None'''
    if tstr:
        return tstr.strip()
    return ''

def set_if_notempty(value, key):
    "Sets to value key, if key isn't empty"
    if key:
        value = key


def get_authors(node, messages=None):
    '''
    Creates or finds authors, returns authors list
    Appends warning, error to messages
    '''
    if messages == None:
        messages = []
    authors = []

    for author_node in node.getchildren():
        author = None
        is_created_global = False

        # TODO add by id 

        # look in tag author
        for details_node in author_node.getchildren():
            # create or find author with name from tag
            if details_node.tag == 'name':
                author_name = strip_str(details_node.text)
                if author_name:
                    (author, is_created) = \
                        Author.objects.get_or_create(name=author_name)
                    # is someone created
                    is_created_global |= is_created

            if details_node.tag == 'alias' and author:
                alias_name = strip_str(details_node.text)
                if alias_name:
                    alias = AuthorAlias.objects.get_or_create(name=alias_name)[0]
                    author.alias.add(alias)
        # add author to list, if it is created or found
        if author:
            authors.append(author)
        else:
            analyzer_log.warning("One author is not added. (Empty name)")
            messages.append(('warning',
                            "One author is not added. (Empty name)"))
    return (authors, is_created_global)



def get_files(node, messages=None):
    '''Creates or finds files, returns files list'''
    if messages == None:
        messages = []
    book_files = []

    for file_node in node.getchildren():
        book_file = None

        # TODO add by id

        # look in tag file
        for details_node in file_node.getchildren():
            # create or find file with link from tag
            if details_node.tag == 'link':
                link = strip_str(details_node.text)
                if link:
                    link_hash = md5(link).hexdigest()
                    book_file = BookFile.objects.get_or_create(link=link,
                                                        link_hash=link_hash)[0]

            # add size filed if exists book_file and size is int
            if details_node.tag == 'size' and book_file:
                size = strip_str(details_node.text)
                try:
                    size = int(size)
                    book_file.size = size
                except ValueError:
                    analyzer_log.warning("size is not integer. \
                       book_file.link='%s'" % (book_file.link))
                
            if details_node.tag == 'type' and book_file:
                file_type = strip_str(details_node.text)
                # TODO check type
                # should I check type, or maybe i should believe
                if file_type:
                    book_file.type = file_type

            if details_node.tag == 'more_info' and book_file:
                set_if_notempty(book_file.more_info,
                                strip_str(details_node.text))

            if details_node.tag == 'img_link' and book_file:
                set_if_notempty(book_file.img_link,
                                strip_str(details_node.text))

        # add book_file to list, if it is created or found
        if book_file:
            book_file.save()
            book_files.append(book_file)
        else:
            analyzer_log.warning("One book_file is not added. (Empty link)")
            messages.append(('warning',
                            "One book_file is not added. (Empty link)"))
    return book_files


def get_book_inf(xml, messages=None):
    '''
    Reads information from xml, finds or creates the book author,
    the book files, annotations, etc

    Returns tupel of 
    (NOT saved models.Book with information about it in its fileds,
    list of authors, list of book files, list of annotations)

    Or raises InputDataServerException, if the book title not found.
    '''
    if messages == None:
        messages = []

    book = Book(title='', lang='')
    authors = []
    book_files = []
    annotations = []

    # unused flag
    #is_author_created = False

    for node in xml.getchildren():
        if node.tag == 'title':
            book.title = strip_str(node.text)

        if node.tag == 'lang':
            book.language = get_language(node.text)

        if node.tag == 'authors' and book.title:
            (authors, is_author_created) = get_authors(node, messages)

        if node.tag == 'files' and book.title:
            book_files = get_files(node)
        
        if node.tag == 'annotation' and book.title:
            annotation_txt = strip_str(node.text)
            if annotation_txt:
                annotation = \
                    Annotation.objects.get_or_create(name=annotation_txt)[0]
                annotations.append(annotation)

    # if there are not the title of the book, raise exception
    if not book.title:
        analyzer_log.warning('In request there is not the title of the book')
        raise InputDataServerException(
           'In request there is not the title of the book')
    # if there are not the book_file, raise exception
    elif not book_files:
        analyzer_log.warning('In request there is not the book_file')
        raise InputDataServerException('In request there is not the book_file')

    return (book, authors, book_files, annotations)


def save_book_inf(book, authors, book_files, annotations):
    '''
    Trys to find book by title and its authors.
    Creates book, if not found.
    Adds all information to book, saves it to database.
    '''
    messages = []

    # try to find the book by this authors
    found_books = Book.objects.filter(title=book.title)
    if book.lang:
        found_books = found_books.filter(lang__in=[book.lang, ''])
    for author in authors:
        found_books = found_books.filter(author=author)

    found_book_in_db = None
    # find book with the same numbers of authors
    for found_book in found_books:
        if found_book.author.count() == len(authors):
            found_book_in_db = found_book

    if found_book_in_db:
        # set lang to book
        if book.lang:
            found_book_in_db.lang = book.lang
            found_book_in_db.save()

        book = found_book_in_db
        messages.append(('info', 'Book updated'))
    else:
        # not found the book in database, then save it

        # TODO do something with language
        # TODO remove it temporary solution
        try:
            language = Language.objects.get(short=book.lang)
        except ObjectDoesNotExist:
            language = Language.objects.get(short='?')
        book.language = language

        book.save()
        messages.append(('info', 'Book created'))

    messages.append(('info', 'book.id=%i' % (book.id)))

            
    # add authors, book_files, annotations to the book
    for author in authors:
        book.author.add(author)

    for book_file in book_files:
        book.book_file.add(book_file)

    for annotation in annotations:
        book.annotation.add(annotation)

    return messages


def xml_exec_insert_unsafe(xml):
    "Insert xml request to database, returns list of warning strings"

    messages = []
    
    #if xml.tag != 'book':
    #    raise InputDataServerException("Not found root tag 'book'")

    # get infromation about the book from the request
    (book, authors, book_files, annotations) = get_book_inf(xml, messages)

    # save infomation to database
    save_messages = save_book_inf(book, authors, book_files, annotations)

    for msg in save_messages:
        messages.append(msg)

    MAIN_LOG.info("Added book " + book.title)
    
    return messages


@transaction.commit_manually
def xml_exec_insert(xml):
    '''
    Executes xml request for insert to database.
    Returns list of warning, error messages.
    '''
    try:
        messages = xml_exec_insert_unsafe(xml)
    except:
        transaction.rollback()
        raise
    transaction.commit()
    messages.append(('DEBUG', "transaction.commit()"))

    return messages



