""" search module """
# -*- coding: utf-8 -*-

from django.db.models import Q

from book.models import Book, Tag
from django.template import RequestContext

from book.search_engine.sphinx_engine import SphinxSearchEngine

from views import available_languages, render_response
from django.core.paginator import Paginator, InvalidPage, EmptyPage

# type of search engine
SEARCH_ENGINE = SphinxSearchEngine()

def simple_search(request, response_type, items_per_page, page, start_index):
    """ simple search with query """
    tags = Tag.objects.all().order_by("name")
    request_string = ""
    for (k, v) in request.GET.iteritems():
        if k != 'page':
            request_string += (k + "=" + v + "&")
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

    if response_type == "atom":
        return render_response(request, 'book/opds/search_response.xml',
            {'books': books[start_index:start_index+items_per_page], 
            'query': query, 'curr': page, 'items_per_page': items_per_page, 
            'total':total, 'next':next, },
            context_instance=RequestContext(request))
        
    if response_type == "xhtml":
        return render_response(request, 'book/xhtml/search_response.xml',
            {'books': books,'items_per_page': items_per_page, 'query': query,
            'tags': tags, 'authors': authors, 'suggestions':books.suggestion, 'request_string': request_string, }, 
            context_instance=RequestContext(request))

def search_in_author(request, lang, tag, response_type, items_per_page, page, 
                                start_index, main_title):
    ''' search only by authors'''
    tags = Tag.objects.all().order_by("name")
    langs = available_languages()
    author = request.GET['author']

    if not author:
        return no_results(request, response_type, main_title)

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
    if response_type == "atom":
        return render_response(request, 'book/opds/authors_search_response.xml',
            {'authors': authors[start_index:start_index+items_per_page],
            'title': main_title,  'curr': page, 'next':next, 'author': author, 
            'items_per_page':items_per_page, 'total':total })
    if response_type == "xhtml":
        return render_response(request, 'book/xhtml/authors_search_response.xml',
            {'authors': authors, 'author': author, 'title':main_title,
            'items_per_page':items_per_page, 'tags': tags, 'langs':langs,
            'suggestions':authors.suggestion}, 
            context_instance=RequestContext(request))


def search_request_to_server(request, response_type, is_all):
    """ builds opds and xhtml response for search request"""
    tags = Tag.objects.all().order_by("name")
    langs = available_languages("")
    request_to_server = Q()
    main_title = {}
    suggestions = None
    
    page, start_index, items_per_page = 1, 0, 20
    title = author = tag = lang = None
    #books = Book.objects.none()

    # initialization
    request_string = ""
    for (k, v) in request.GET.iteritems():
        if k != 'page':
            request_string += (k + "=" + v + "&")
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
        if tag[len(tag)-8:] == u": прочее":
            t = Tag.objects.get(name=tag[0:len(tag)-8])
            t_childs = Tag.objects.filter(Q(Q(parent__name=t.name) & Q(credit=1)))
            q = Q(tag=t)
            for tt in t_childs:
                q = Q(q & ~Q(tag=tt))
            request_to_server = request_to_server & q
        else:
            request_to_server = request_to_server & Q(tag__name=tag)
        main_title['tag'] = tag

    # main logic
    if 'query' in request.GET and request.GET['query']:
        # search in title, author.name, alias, annotation
        return simple_search(request, response_type, items_per_page, page, 
                                start_index)
    if title:
        main_title['tit'] = title
        if author:
            main_title['author'] = author    
        books = SEARCH_ENGINE.book_search(title=title, author=author, tag=tag, 
                                            lang=lang)   
        suggestions = books.suggestion       
    
    elif author:
        return search_in_author(request, lang, tag, response_type, 
                                items_per_page, page, start_index, main_title)
    else:
        total = Book.objects.filter(request_to_server).distinct().count()
        books = Book.objects.filter(request_to_server).distinct()[start_index:start_index + items_per_page]
    if not books:
        return no_results(request, response_type, main_title, suggestions)

    if is_all == "yes":
        books = Book.objects.all()

    #books = books[:20]
    #total = len(books)

    next = None
    max_item = items_per_page * page
    if (total - 1) / max_item != 0:
        next = page + 1
    pages = total / items_per_page

    if response_type == "atom":
        return render_response(request, 'book/opds/search_response.xml',
            {'books': books[start_index:start_index+items_per_page],
            'title': main_title,  'curr': page, 'next':next,
            'items_per_page':items_per_page, 'total':total })
        
    if response_type == "xhtml":
        return render_response(request, 'book/xhtml/search_response.xml',
            {'books': books, 'title': main_title,
            'items_per_page':items_per_page, 'tags': tags, 'langs':langs,
            'suggestions':suggestions, 'has_previous':page>1, 'show_first':page!=1,
            'has_next':page<pages,
            'page_numbers': [x for x in range(page-3, page+4) if x > 0 and x <= pages],
            'page': page,
            'show_last':page<pages-3 and pages>0, 'next':page+1, 'previous':page-1,
            'pages': pages,
            'request_string': request_string,
            },
            context_instance=RequestContext(request))


def no_results(request, response_type, main_title, suggestions, is_simple = False):
    ''' returns 'no result' message'''
    tags = Tag.objects.all().order_by("name")
    langs = available_languages("")

    if response_type == "atom":
        return render_response(request, 'book/opds/no_results.xml', 
                                    {'is_simple': is_simple, 'query': main_title,
                                    'suggestions':suggestions, 'tags': tags, 
                                    'langs':langs})
    if response_type == "xhtml":
        if is_simple:
            return render_response(request, 'book/xhtml/no_results.xml', 
                                        {'is_simple': is_simple, 'query': main_title,
                                        'suggestions':suggestions, 'tags': tags, 
                                        'langs':langs})
        else:
            return render_response(request, 'book/xhtml/no_results.xml', 
                                        {'is_simple': is_simple, 'title': main_title,
                                        'suggestions':suggestions, 'tags': tags, 
                                        'langs':langs})

def quick_search(request, response_type, items_per_page, page, start_index):
    pass
