# -*- coding: utf-8 -*-
from book.models import Book, Author, Tag, Language, EpubBook, BookFile
from spec.langcode import LANG_CODE
from urllib import quote, unquote
from django.db.models import Q

import views
from views import render_response

def catalog(request):
    """builds opds response for catalog request"""
    return render_response(request, 'book/opds/libru/catalog.xml')


def books_by_authors(request):
    """builds opds response for authors by letter request"""
    if 'letter' in request.GET and request.GET['letter']:
        return authors_by_one_letter(request)
    else:
        return authors_by_two_letters(request)

def generate_alphabets():
    alphabet_string = views.generate_russian_alphabet()
    alphabet_string += views.generate_latin_alphabet()
    return alphabet_string

def authors_by_one_letter(request):
    '''returns authors arranged by first letter in their names'''
    letter = unquote(request.GET['letter'])
    alphabet_string = generate_alphabets()
    string = ""
    for let in alphabet_string:
        request_to_server = Q(book__pagelink__startswith="http://lib.ru", name__istartswith=letter + let)
        auth_count = Author.objects.filter(request_to_server).distinct().count()
        if auth_count > 0:          # TODO condition
            string += let
    string = string[0:-1]

    if len(string) < 1:
        request_to_server = Q(book__pagelink__startswith="http://lib.ru", name__istartswith=letter)
        authors = Author.objects.filter(request_to_server).distinct().\
                                                            order_by('name')
        return render_response(request, 'book/opds/libru/books_by_author.xml',
            {'authors': authors})

    my_list = []
    if letter in views.generate_russian_alphabet():
        my_string = letter + u'а'
    else:
        my_string = letter + 'a'

    for let in string:
        if my_string != letter + let:
            my_string += "-" + letter + let
        my_list.append(my_string)
        my_string = letter + unichr(ord(let) + 1)
    if letter in views.generate_russian_alphabet():
        my_string += "-" + letter + u"я"
    else:
        my_string += "-" + letter + "z"

    my_list.append(my_string)

    return render_response(request, 'book/opds/libru/books_by_author.xml',
        {'string': my_list, 'num': 2, 'letter': letter })

def authors_by_two_letters(request):
    '''returns authors arranged by first two letters in their names'''
    if 'letters' in request.GET and request.GET['letters']:
        letters = unquote(request.GET['letters'])
        try:
            start = generate_alphabets().index(letters[1].lower())
            end = generate_alphabets().index(letters[4].lower()) + 1
            my_let = generate_alphabets()[start:end]

            request_to_server = Q()
            for let in my_let:
                request_to_server = request_to_server | \
                                    Q(book__pagelink__startswith="http://lib.ru", \
                                      name__istartswith=letters[0] + let)
        except (IndexError, ValueError):
            request_to_server = Q(book__pagelink__startswith="http://lib.ru", name__istartswith=letters)

        authors = Author.objects.filter(request_to_server).distinct().\
                                                            order_by('name')

        return render_response(request, 'book/opds/libru/books_by_author.xml',
            {'authors': authors})
    else:
        alphabet_string = generate_alphabets()
        request_to_server = Q()
        string = ""
        for let in alphabet_string:
            request_to_server = Q(book__pagelink__startswith="http://lib.ru", name__istartswith=let)
            authors_count = Author.objects.filter(request_to_server).\
                                                        distinct().count()
            if authors_count != 0:
                string += let
        return render_response(request, 'book/opds/libru/books_by_author.xml',
            {'string': string, 'num': 1 })


def author_request(request, author_id):
    """builds opds esponse for all author's books request"""
    try:
        author = Author.objects.get(id=author_id)
    except ObjectDoesNotExist:
        raise Http404
    books = author.book_set.filter(pagelink__startswith="http://lib.ru")
    return render_response(request, 'book/opds/libru/author.xml',
        {'author': author, 'books': books})


def books_by_language(request):
    """builds opds response for books by lang request"""
    languages = available_languages()

    return render_response(request, 'book/opds/libru/books_by_lang.xml',
        {'languages':languages})

def available_languages():
    '''returns all languages used in books from libru'''
    all_langs = Language.objects.all().exclude(book__isnull=True)
    langs = []
    for lang in all_langs:
        books = lang.book_set.filter(pagelink__startswith="http://lib.ru")
        if books:
            langs.append(lang)
    return langs

def available_tags():
    all_tags = Tag.objects.all().order_by("name")
    tags = []
    for tag in all_tags:
        books = tag.book_set.filter(pagelink__startswith="http://lib.ru")
        if books:
            tags.append(tag)
    return tags


def books_by_tags(request):
    """builds opds response for books by tags request"""
    tags = available_tags()
    languages = available_languages()
    return render_response(request, 'book/opds/libru/books_by_tag.xml',
        {'tags':tags, 'languages':languages})



from book.search_engine.sphinx_engine import SphinxSearchEngine
SEARCH_ENGINE = SphinxSearchEngine()

def simple_search(request, response_type, items_per_page, page, start_index):
    """ simple search with query """
    tags = available_tags()
    query = request.GET['query']
    if not query:
        return no_results(request, response_type, query, None, is_simple = True)

    books = SEARCH_ENGINE.simple_search(query)

    authors = SEARCH_ENGINE.author_search(author=query, max_length=5)

    if not books and not authors:
        return no_results(request, response_type, query, books.suggestion, is_simple = True)


    total = len(books)

    next = None
    max_item = items_per_page * page
    if (total-1)/max_item != 0:
        next = page+1

    return render_response(request, 'book/opds/libru/search_response.xml',
            {'books': books[start_index:start_index+items_per_page],
            'query': query, 'curr': page, 'items_per_page': items_per_page,
            'total':total, 'next':next, },
            context_instance=RequestContext(request))


def search_in_author(request, lang, tag, items_per_page, page,
                                start_index, main_title):
    ''' search only by authors'''
    tags = available_tags()
    langs = available_languages()
    author = request.GET['author']

    if not author:
        return no_results(request, main_title)

    main_title['author'] = author

    #TODO language in author_search
    authors = SEARCH_ENGINE.author_search(author=author, lang=lang, tag=tag,
                                            max_length=10)
    if not authors:
        return no_results(request, response_type, main_title, authors.suggestion)

    total = len(authors)
    next = None
    max_item = items_per_page * page
    if (total-1)/max_item != 0:
        next = page+1
    return render_response(request, 'book/opds/libru/authors_search_response.xml',
        {'authors': authors[start_index:start_index+items_per_page],
        'title': main_title,  'curr': page, 'next':next, 'author': author,
        'items_per_page':items_per_page, 'total':total })



def search_request_to_server(request):
    """ builds opds  response for search request"""
    tags = available_tags()
    langs = available_languages()
    request_to_server = Q(pagelink__startswith='http://lib.ru')
    main_title = {}
    suggestions = None

    page, start_index, items_per_page = 1, 0, 20
    title = author = tag = lang = None
    books = Book.objects.none()

    # initialization
    if 'items_per_page' in request.GET and request.GET['items_per_page']:
        items_per_page = int(request.GET['items_per_page'])

    if 'page' in request.GET and request.GET['page']:
        page = int(request.GET['page'])
        start_index = items_per_page * (page - 1)

    if 'title' in request.GET and request.GET['title']:
        title = request.GET['title']

    if 'author' in request.GET and request.GET['author']:
        author = request.GET['author']

    if 'lang' in request.GET and request.GET['lang']:
        lang = request.GET['lang']
        request_to_server = request_to_server & Q(language__short=lang)
        main_title['lang'] = lang

    if 'tag' in request.GET and request.GET['tag']:
        tag = request.GET['tag']
        request_to_server = request_to_server & Q(tag__name__icontains=tag)
        main_title['tag'] = tag

    # main logic
    if 'query' in request.GET and request.GET['query']:
        # search in title, author.name, alias, annotation
        return simple_search(request, items_per_page, page,
                                start_index)
    if title:
        main_title['tit'] = title
        if author:
            main_title['author'] = author
        books = SEARCH_ENGINE.book_search(title=title, author=author, tag=tag,
                                            lang=lang)
        suggestions = books.suggestion

    elif author:
        return search_in_author(request, lang, tag, items_per_page, page, start_index, main_title)
    else:
        books = Book.objects.filter(request_to_server).distinct()

    if not books:
        return no_results(request, main_title, suggestions)

    total = len(books)

    next = None
    max_item = items_per_page * page
    if (total-1)/max_item != 0:
        next = page+1

    return render_response(request, 'book/opds/libru/search_response.xml',
            {'books': books[start_index:start_index+items_per_page],
            'title': main_title,  'curr': page, 'next':next,
            'items_per_page':items_per_page, 'total':total })


def no_results(request, main_title, suggestions, is_simple = False):
    ''' returns 'no result' message'''
    tags = Tag.objects.all().order_by("name")
    langs = available_languages()

    return render_response(request, 'book/opds/libru/no_results.xml',
                                {'is_simple': is_simple, 'query': main_title,
                                'suggestions':suggestions, 'tags': tags,
                                'langs':langs})
