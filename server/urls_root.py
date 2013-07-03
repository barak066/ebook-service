from django.conf.urls.defaults import * 
from django.contrib import admin
from django.conf import settings

from book.views import who, analyzer_view

from django.conf.urls.defaults import url


urlpatterns = patterns('',
    #home
    (r'^$', 'views.catalog',
        {'response_type': 'xhtml',}),

    # interface for analizer/crawler
#    (r'^data/get/?$', data_modify, {'action': ACTION['get'],}),
#    (r'^data/insert/?$', data_modify, {'action': ACTION['insert'],}),
    (r'^data/?$', who),
    # new interface for analyzer
    (r'^data/search/?$', analyzer_view, {'action': 'SEARCH'},),
    (r'^data/modify/?$', analyzer_view, {'action': 'MODIFY'},),


    # interface for search
    (r'^search.atom/?$', 'search_views.search_request_to_server',
        {'response_type': 'atom', 'is_all': 'no'}),
    (r'^search/?$', 'search_views.search_request_to_server',
        {'response_type': 'xhtml', 'is_all': 'no'}),
        
    #all books
    (r'^all.atom/?$', 'search_views.search_request_to_server',
        {'response_type': 'atom', 'is_all': 'yes'}),
    (r'^all/?$', 'search_views.search_request_to_server',
        {'response_type': 'xhtml', 'is_all': 'yes'}),
    
    # requests
    (r'^book.atom/id(\d{1,})/?$', 'views.book_request',
        {'response_type': 'atom',}),
    (r'^book/id(\d{1,})/?$', 'views.book_request',
        {'response_type': 'xhtml',}),
    
    (r'^author.atom/id(\d{1,})/?$', 'views.author_request',
        {'response_type': 'atom',}),
    (r'^author/id(\d{1,})/?$', 'views.author_request',
        {'response_type': 'xhtml',}),
    
    #book catalog
    (r'^catalog.atom/?$', 'views.catalog',
        {'response_type': 'atom',}),
    (r'^catalog/?$', 'views.catalog',
        {'response_type': 'xhtml',}),
    
    #books sorted by authors, languages, subjects
    (r'^discover/authors.atom/?$', 'views.books_by_authors',
        {'response_type': 'atom',}),
    (r'^discover/authors/?$', 'views.books_by_authors',
        {'response_type': 'xhtml',}),
        
    (r'^discover/languages.atom/?$', 'views.books_by_language',
        {'response_type': 'atom',}),
    (r'^discover/languages/?$', 'views.books_by_language',
        {'response_type': 'xhtml',}),
        
    (r'^discover/subjects.atom/?$', 'views.books_by_tags',
        {'response_type': 'atom',}),
    (r'^discover/subjects/?$', 'views.books_by_tags',
        {'response_type': 'xhtml',}),
        
    (r'^simple_search/?$', 'views.simple_search'),
    (r'^extended_search/?$', 'views.extended_search'),
    
    #libru opds
    #all views' code is almost copy-pasted (with little changes) from views and search_views
    (r"^libru/", include("libru_urls")),

    #magazines
    (r'^magazines/', include('magazines.urls')),
    
    #admin
#    (r'^admin/book/author/(.*)/$', 'book.templatetags.book_tags.author'),      #my admin view for author

    (r'^admin/', include(admin.site.urls)),
#    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    #opensearchdescription
    (r'^opensearch/?$', 'views.opensearch_description'),
    
    #user_information
#    (r'^user/insert/?$', 'reader.views.insert_user_information'),
    
    #openid
#    (r'^$', 'django.views.generic.simple.direct_to_template',
#        {'template': 'home.html'}),
    #(r'^account/', include('django_authopenid.urls')),

    #media 
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': 'media'}),

    url(r'^extended_search/autocomplete_title/?$', 'views.autocomplete_title', name='autocomplete_title'),
    url(r'^extended_search/autocomplete_author/?$', 'views.autocomplete_author', name='autocomplete_author'),
    (r'^i18n/', include('django.conf.urls.i18n')),

    #epuber
    (r'^epub/$', 'views.add_book'),
    (r'^epub/create/doc/$', 'views.add_doc_form'),
    (r'^epub/create/txt/$', 'views.epub_form'),
    (r'^register/$', 'views.register'),
    (r'^from/lib/ru/$', 'views.get_book_from_libru'),

    (r'^account/signin/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', 'django.contrib.auth.views.logout'),
    (r'^accounts/profile/$', 'views.profile'),

    #sentry
    (r'^sentry/', include('sentry.urls')),

    #favicon
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/' + settings.MEDIA_URL + '/pic/favicon.ico'}),
    (r'^ajax/authors$', 'views.ajax'),

    (r'^localeurl/', include('localeurl.urls')),

)

urlpatterns += patterns('',
    (r'^spellcheck/$', 'views.spellcheck'), 
)

handler404 = 'views.my_404_view'
handler500 = 'views.my_404_view'