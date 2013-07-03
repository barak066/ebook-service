from django.conf.urls.defaults import *
__author__ = 'dima'

urlpatterns = patterns('views',
    (r'^catalog.atom/?$', 'catalog',
        {'site': 'libru', 'response_type': 'atom'}),
    (r'^author.atom/id(\d{1,})/?$', 'author_request',
        {'site': 'libru', 'response_type': 'atom'}),
    (r'^discover/authors.atom/?$', 'books_by_authors',
        {'site': 'libru', 'response_type': 'atom'}),
    (r'^discover/languages.atom/?$', 'books_by_language',
        {'site': 'libru', 'response_type': 'atom'}),
    (r'^discover/subjects.atom/?$', 'books_by_tags',
        {'site': 'libru', 'response_type': 'atom'}),
    (r'^search.atom/?$', 'search_request_to_server',
        {'site': 'libru', 'response_type': 'atom'}),
)