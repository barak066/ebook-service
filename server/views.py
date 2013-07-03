"""opds and xhtml view"""
# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist

from django.shortcuts import render_to_response
from django.utils.translation import gettext_lazy as _

from book.models import Book, Author, Tag, Language, EpubBook, BookFile
from settings import EBST_NAME, EBST_VERSION, EBST_VERSION_BUILD, MEDIA_URL
from django.template import RequestContext

from django.http import Http404
from django.http import HttpResponse

from django.db.models import Q

from forms.views_forms import ExtendedSearch, DocCreateForm, EpubAddForm
from forms.views_forms import available_languages

from django.utils import simplejson
import httplib

import os, re, shutil

from django.core.files.uploadedfile import UploadedFile

from django.contrib.auth.forms import UserCreationForm
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from spec.langcode import LANG_CODE

from django.conf import settings

from epuber.epub import Book as BookCreator
from epuber.epub import BookProperties
from epuber.doc import DocParser
from epuber.LibRuParser import LibRuParser
from urllib import quote, unquote
import tempfile
from server.search_views import *
from settings import RESULTS_PER_PAGE

GOOGLE_URL = "www.google.com"

def make_links(book):
    """
    Returns lib.ru links for book
    """
    books = book.book_file.filter(link__contains="http://lib.ru")
    links = []
    for temp_book in books:
        links.append("/from/lib/ru/?link=" + quote(temp_book.link))
    return links

def book_request(request, book_id, response_type):
    """ builds opds and xhtml response for book id request"""
    try:
        book = Book.objects.get(id=book_id)
    except ObjectDoesNotExist:
        raise Http404

    links = make_links(book)
    sims = book.similar.all()
    if response_type == "atom":
        return render_response_atom(request, 'book/opds/book.xml',
                               {'book': book, 'links': links})

    if response_type == "xhtml":
        return render_response(request, 'book/xhtml/book.xml',
                               {'book': book, 'links': links, 'sims': sims })

def author_request(request, author_id, response_type, site=""):
    """builds opds and xhtml response for all author's books request"""
    try:
        author = Author.objects.get(id=author_id)
    except ObjectDoesNotExist:
        raise Http404
    if site == "libru":
        books = author.book_set.filter(pagelink__startswith="http://lib.ru")
    else:
        books = author.book_set.all()
    if response_type == "atom":
        return render_response_atom(request, 'book/opds/author.xml',
        {'author': author, 'books': books})
    if response_type == "xhtml":
        return render_response(request, 'book/xhtml/author.xml',
        {'author': author, 'books': books})

def opensearch_description(request):
    """returns xml open search description"""
    return render_response(request, "data/opensearchdescription.xml", )
    
def catalog(request, response_type, site = ""):
    """
    builds opds and xhtml response for catalog request
    """
    #if site and site == "libru":
    #    return render_response(request, 'book/opds/libru/catalog.xml')

    if response_type == "atom":
        return render_response_atom(request, 'book/opds/catalog.xml')
    if response_type == "xhtml":
        return render_response(request, 'book/xhtml/catalog.xml')

def generate_alphabet(first, last):
    """
    Generates all symbols from first to last
    """
    alphabet_string = u""
    firstn = ord(first)
    lastn = ord(last) + 1
    for ch in range(firstn, lastn):
        letter = unichr(ch)    # в этой строке важна функция unichr
        alphabet_string += letter
    return alphabet_string

def generate_latin_alphabet():
    """
    Generates latin alphabet
    """
    return generate_alphabet(u'a', u'z')

def generate_russian_alphabet():
    """
    Generates russian alphabet
    """
    return generate_alphabet(u'а', u'я')

def generate_alphabets():
    alphabet_string = generate_russian_alphabet()
    alphabet_string += generate_latin_alphabet()
    return alphabet_string
        
def authors_by_one_letter(request, response_type, site=""):
    '''
    Returns authors arranged by first letter in their names
    '''
    add_request = Q()
    if site and site == 'libru':
        add_request = Q(book__pagelink__startswith="http://lib.ru")
    letter = unquote(request.GET['letter'])
    alphabet_string = generate_alphabets()
    string = []
    for let in alphabet_string:
        request_to_server = add_request & Q(name__istartswith=letter + let)
        auth_count = Author.objects.filter(request_to_server).distinct().count()
        count = int(auth_count)
        if auth_count > 0:          # TODO condition
            string.append((let, count))

    #string = string[0:-1]
    
    if len(string) < 1:
        request_to_server = add_request & Q(name__istartswith=letter)
        authors = Author.objects.filter(request_to_server).distinct().\
                                                            order_by('name')
        if site and site == "libru":
            return render_response(request, 'book/opds/libru/books_by_author.xml',
                {'authors': authors})

        if response_type == "atom":
            return render_response_atom(request, 'book/opds/books_by_author.xml',
            {'authors': authors})
        if response_type == "xhtml":
            return render_response(request, 'book/xhtml/books_by_author.xml',
            {'authors': authors})
    
    my_list = []
    if letter in generate_russian_alphabet():
        my_string = letter + u'а'
    else:
        my_string = letter + u'a'

    for let in string:
        if my_string != letter + let[0]:
            my_string += "-" + letter + let[0]
        my_list.append((my_string, let[1]))
        my_string = letter + unichr(ord(let[0]) + 1)
    if letter in generate_russian_alphabet():
        my_string += "-" + letter + u"я"
        my_list.append((my_string, 1))
    else:
        my_string += "-" + letter + u"z"
        my_list.append((my_string, 1))

    #if site and site == "libru":
    #    return render_response(request, 'book/opds/libru/books_by_author.xml',
    #        {'string': my_list, 'num': 2, 'letter': letter })

    if response_type == "atom":
        return render_response_atom(request, 'book/opds/books_by_author.xml',
        {'strings': [my_list], 'num': 2, 'letter': letter})
    if response_type == "xhtml":
        return render_response(request, 'book/xhtml/books_by_author.xml',
        {'strings': [my_list], 'num': 2 })

def authors_by_two_letters(request, response_type, site=""):
    '''
    Returns authors arranged by first two letters in their names
    '''
    add_request = Q()
    if site == "libru":
        add_request = Q(book__pagelink__startswith="http://lib.ru")
    if 'letters' in request.GET and request.GET['letters']:
        letters = unquote(request.GET['letters'])
        try:
            start = generate_alphabets().index(letters[1].lower())
            end = generate_alphabets().index(letters[4].lower()) + 1
            my_let = generate_alphabets()[start:end]
            
            request_to_server = Q()
            for let in my_let:
                request_to_server = (request_to_server | \
                                    Q(name__istartswith=letters[0] + let) )& \
                                    add_request
        except (IndexError, ValueError):
            request_to_server = Q(name__istartswith=letters) & \
                                add_request

        authors = Author.objects.filter(request_to_server).distinct().\
                                                            order_by('name')

        if response_type == "atom":
            return render_response_atom(request, 'book/opds/books_by_author.xml',
            {'authors': authors})
        if response_type == "xhtml":
            return render_response(request, 'book/xhtml/books_by_author.xml',
            {'authors': authors})
    else:
        alphabets = [generate_russian_alphabet().upper(), generate_latin_alphabet().upper()]

        strings = [[], []]
        for i, alphabet in enumerate(alphabets):
            for let in alphabet:
                request_to_server = Q(name__istartswith=let)
                authors_count = Author.objects.filter(request_to_server).\
                                                        distinct().count()
                if authors_count != 0:
                    strings[i].append((let, authors_count))
        if response_type == "atom":
            return render_response_atom(request, 'book/opds/books_by_author.xml',
                {'strings': strings, 'num': 1})
        if response_type == "xhtml":
            return render_response(request, 'book/xhtml/books_by_author.xml',
                {'strings': strings, 'num': 1 })

def books_by_authors(request, response_type, site=""):
    """
    builds opds and xhtml response for authors by letter request
    """

    if 'letter' in request.GET and request.GET['letter']:
        return authors_by_one_letter(request, response_type, site)
    else:
        return authors_by_two_letters(request, response_type, site)
                    
def books_by_language(request, response_type, site=""):
    """
    builds opds and xhtml response for books by lang request
    """
    languages = available_languages(site)
    comparator = lambda x, y: Book.objects.filter(language=y).count() - \
                              Book.objects.filter(language=x).count()
    languages = sorted(languages, cmp=comparator)
    
    if response_type == "atom":
        return render_response_atom(request, 'book/opds/books_by_lang.xml',
        {'languages':languages})
    if response_type == "xhtml":
        return render_response(request, 'book/xhtml/books_by_lang.xml',
        {'languages':languages})

def available_tags():
    all_tags = Tag.objects.all().order_by("name")
    tags = []
    for tag in all_tags:
        books = tag.book_set.filter(pagelink__startswith="http://lib.ru")
        if books:
            tags.append(tag)
    return tags


def books_by_tags(request, response_type, site=""):
    """builds opds and xhtml response for books by tags request"""
    add_request = Q()
    book_add_req = Q()
    all_tags = Tag.objects.all()
    if site == "libru":
        add_request = Q(book__pagelink__startswith="http://lib.ru")
        book_add_req = Q(pagelink__startswith="http://lib.ru")
        all_tags = available_tags()
    
    tags_top = []
    for tag in all_tags:
        if tag.credit == 2:
            tags_top.append(tag)
    tags_sub = {}
    for t in tags_top:
        num = Book.objects.filter(Q(tag=t) & book_add_req).count()

        tempt = []
        for tag in all_tags:
            if tag.parent == t and tag.credit == 1:
                tempt.append(tag)
        tempt = sorted(tempt, key = lambda x: x.name)
        first_level = Q(parent__name=t.name) & add_request
        second_level = Q(parent__parent__name=t.name) & add_request
        third_level = Q(parent__parent__parent__name=t.name) & add_request
        req = (first_level | second_level | third_level) & Q(credit=-1)
        
        tempt_sub = Tag.objects.filter(req).order_by("name")
        tempt1 = []
        for st in tempt:
            tempt1.append( (st, Book.objects.filter(Q(tag=st) & book_add_req).count()) )
            
        q = Q(tag=t) & book_add_req
        for tt in tempt:
            q = q & ~Q(tag=tt)
        tempt1.append( (None, Book.objects.filter(q).count()) )
        tempt1_sub = []
        for st in tempt_sub:
            tempt1_sub.append( (st, Book.objects.filter(tag=st).count()) )
        tags_sub[(t, num)] = (tempt1, tempt1_sub)
    languages = available_languages(site)

    tags = []
    for tag in tags_sub:
        tags.append(tag[0].name)
    if response_type == "atom":
        return render_response_atom(request, 'book/opds/books_by_tag.xml',
        {'tags':tags, 'languages':languages})
    if response_type == "xhtml":
        return render_response(request, 'book/xhtml/books_by_tag.xml',
        {'tags_sub':sorted(tags_sub.iteritems(), key = lambda ((k, n), v): k.name), 'languages':languages})
        
def simple_search(request):
    """go to search page"""
    return render_response(request, 'book/xhtml/simple_search.xml')

def extended_search(request, site=""):
    """ extended search """
    tags = Tag.objects.all().order_by("name")
    langs =available_languages(site)
    return render_response(request, 'book/xhtml/extended_search.xml', {'tags': tags,
                                'langs': langs,})

def render_response(req, *args, **kwargs):
    bottom_string = "%s v%s (r%s)" % (EBST_NAME, EBST_VERSION, 
                                                        EBST_VERSION_BUILD)
    google_link = 'http://code.google.com/p/ebook-service'

    kwargs['context_instance'] = RequestContext(req, 
                    {'bottom_string':bottom_string, 'google_link':google_link})

    return render_to_response(*args, **kwargs)

def render_response_atom(req, *args, **kwargs):
    bottom_string = "%s v%s (r%s)" % (EBST_NAME, EBST_VERSION, 
                                                        EBST_VERSION_BUILD)
    google_link = 'http://code.google.com/p/ebook-service'

    kwargs['context_instance'] = RequestContext(req, 
                    {'bottom_string':bottom_string, 'google_link':google_link})
    kwargs['mimetype'] = "application/atom+xml"

    return render_to_response(*args, **kwargs)
    

def autocomplete_title(request):
    def results_to_string(results):
        if results:
            for r in results:
                yield '%s|%s\n' % (r.title, r.pk)

    query = request.REQUEST.get('q', None)
    author = request.REQUEST.get('author', None)

    if query:
        books = Book.objects.filter(title__istartswith=query)
    else:
        books = Book.objects.all()
    if author:
        books = books.filter(author__name__istartswith=author)        

    books = books[:15]
#    books = books[:int(request.REQUEST.get('limit', 15))]
    return HttpResponse(results_to_string(books), mimetype='text/plain')

def autocomplete_author(request):
    def results_to_string(results):
        if results:
            for r in results:
                yield '%s|%s\n' % (r.name, r.pk)

    query = request.REQUEST.get('q', None)

    if query:
        authors = Author.objects.filter(name__istartswith=query)
    else:
        authors = Author.objects.none()

    authors = authors[:15]
#    books = books[:int(request.REQUEST.get('limit', 15))]
    return HttpResponse(results_to_string(authors), mimetype='text/plain')


def spellcheck(request):
    '''
        function for spellcheck annotation in admin
    '''
    if request.method == 'POST':
        lang = request.GET.get("lang", "en")
        data = request.raw_post_data
        con = httplib.HTTPSConnection(GOOGLE_URL)
        con.request("POST", "/tbproxy/spell?lang=%s" % lang, data)
        response = con.getresponse()
        r_text = response.read()
        con.close()
        return HttpResponse(r_text, mimetype='text/javascript')


# epuber
class _ExistingFile(UploadedFile):
    ''' Utility class for importing existing files to FileField's. '''

    def __init__(self, path, *args, **kwargs):
        self.path = path
        super(_ExistingFile, self).__init__(*args, **kwargs)

    def temporary_file_path(self):
        return self.path

    def close(self):
        pass

    def __len__(self):
        return 0
    
    def __str(self):
        return super.__str__

@login_required
def epub_form(request):
    """
    Displays form for converting from txt files and adding into db
    """
    messages = []
    if request.method == "POST":
        form = EpubAddForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            book_name = cd['caption']
            lang = cd['language']
            tags = cd['tags']
            subject = cd['subject']
            description = cd['description']
            type = cd['type']
            date = cd['date']
            rights = cd['rights']
            
            temp_name = tempfile.mkstemp()[1]
            properties = BookProperties(temp_name, book_name)
            properties.language = lang
            properties.subject = subject
            properties.description = description
            properties.genre = type
            properties.date = date
            properties.rights = rights
            properties.author = request.user.first_name + " " + request.user.last_name
            book = BookCreator(properties)
            file = request.FILES['file']
            toc = cd['toc']
            if toc:
                book.split_by_toc(toc, file.read())
            else:
                book.txt_to_html(file.read(), temp_name + "text.html")
                book.add_file(temp_name + "text.html", "c1", "")
                
            book.pack()

            try:
                language = Language.objects.get(short=lang)
            except:
                return render_response(request, "epub/epub_form.html", 
                                       {'errors': [_('No such language.')],
                                        'user': request.user, 'menu_on': True,
                                        'form': form})

            lang_code = LANG_CODE[0]
            for lang_code in LANG_CODE:
                if lang_code[0] == lang:
                    break
            
            book_model = Book.objects.create(language=language, pagelink="")
            book_model.title = book_name
            try:
                author = Author.objects.get(name=request.user.first_name + 
                                            ' ' + request.user.last_name)
            except:
                author = Author.objects.create(name=request.user.first_name + 
                                            ' ' + request.user.last_name)
            book_model.author = [author]
            book_model.save()
            
            ebook = EpubBook.objects.create(book = book_model)

            exfile = _ExistingFile(temp_name)
            ebook.name.save(book_name + ".epub", exfile)
            print ebook.name
            try:
                book_file = BookFile(link="/" + MEDIA_URL + "/" + quote(str(ebook.name)))
                book_file.type = 'epub'
                book_file.save()
            except Exception, e:
                print e
                return render_response(request, "epub/epub_form.html",
                                       {'errors': [_("Book name should be unique")],
                                        'menu_on': True, 'form': form})
            book_model.book_file = [book_file]
            book_model.save()
            
            
            ebook.save()
            
            messages += [_("Book successfully created.")]
            hrr =  HttpResponseRedirect("/book/id%d" % book_model.id)
            return hrr
    else:
        form = EpubAddForm()

    return render_response(request, "epub/epub_form.html", 
                           {'user': request.user,
                            'menu_on': True, 'form': form,
                            'messages': messages})

@login_required
def add_doc_form(request):
    """
    Displays form for converting and adding book in doc
    """
    if request.method == "POST":
        form = DocCreateForm(request.POST, request.FILES)
        if form.is_valid():
            temp_name = tempfile.mkstemp()[1]
            cd = form.cleaned_data
            properties = BookProperties(temp_name, cd['title'].encode("utf-8"))
            properties.language = cd['language']
            properties.author = request.user.first_name + ' ' + request.user.last_name

            properties.subject = cd['subject'].encode("utf-8")
            properties.description = cd['description'].encode("utf-8")
            properties.genre = cd['type'].encode("utf-8")
            properties.date = cd['date'].encode("utf-8")
            properties.rights = cd['rights'].encode("utf-8")
            properties.author = request.user.first_name + " " + request.user.last_name

            file = request.FILES['file']
            
            doc_file_name = tempfile.mkstemp()[1]
            doc_file = open(doc_file_name, 'wb')
            doc_file.write(file.read())
            doc_file.close()
            doc_parser = DocParser(doc_file_name, properties)
            out_file_name = tempfile.mkdtemp() + "tmp.html"
            doc_parser.parse()

            try:
                language = Language.objects.get(short=cd['language'])
            except:
                return render_response(request, "epub/add_doc_form.html", {'errors': [_('No such language.')],
                                                                      'user': request.user,
                                                                      'menu_on': True,
                                                                           'form': form})

            lang_code = LANG_CODE[0]
            for lang_code in LANG_CODE:
                if lang_code[0] == cd['language']:
                    break
            
            book_model = Book(language=language, title = cd['title'].encode("utf-8"), pagelink="")
            try:
                author = Author.objects.get(name=request.user.first_name + 
                                            ' ' + request.user.last_name)
            except:
                author = Author.objects.create(name=request.user.first_name + 
                                            ' ' + request.user.last_name)
            book_model.save()
            book_model.author = [author]
            
            ebook = EpubBook.objects.create(book=book_model)
            print "creating"
            ebook.name.save(cd['title'].encode("utf-8") + ".epub", _ExistingFile(temp_name))
            

            try:
                book_file = BookFile(link="/" + MEDIA_URL + "/uploads/" + quote(cd['title'].encode("utf-8")) + '.epub')
                book_file.type = 'epub'
                book_file.save()
            except:
                return render_response(request, "epub/add_doc_form.html", 
                                       {'errors': [_("Book name should be unique")],
                                        'menu_on': True, 'form': form})
            book_model.book_file = [book_file]
            book_model.save()
            ebook.save()
            hrr =  HttpResponseRedirect("/book/id%d" % book_model.id)
            return hrr
    else:
        form = DocCreateForm()

    return render_response(request, "epub/add_doc_form.html", {'user': request.user, 'menu_on': True, 'form': form})

@login_required 
def add_book(request):
    """
    Displays "Add Book" page
    """
    return render_response(request, "epub/add_book.html", {'user': request.user,
                                                           'menu_on': True})


def register(request):
    """
    Gets registration form
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()

            user = auth.authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])

            auth.login(request, user)
            return HttpResponseRedirect("/accounts/profile/")
    else:
        form = UserCreationForm()
    return render_response(request, "registration/register.xhtml", {
        'form': form,
        'menu_on': True,
    })

@login_required
def profile(request):
    """
    Gets user profile
    """
    if request.method == "POST": 
        if 'first_name' in request.POST:
            request.user.first_name = request.POST['first_name']
        if 'last_name' in request.POST:
            request.user.last_name = request.POST['last_name']
        request.user.save()

    return render_response(request, "registration/profile.xhtml", {'user': request.user, 
                                                                   'menu_on': True})

def get_book_from_libru(request):
    """
    Gets book from lib.ru in epub
    """
    if request.method == "GET" and 'link' in request.GET:
        errors = []
        if not request.GET['link']:
            errors.append("Empty link")
        if errors:
            return render_response(request, "epub/get_book_from_libru.html", 
                                      {'user': request.user,
                                       'errors': errors,
                                       'menu_on': True})
        else:
            link = request.GET['link']
            regex = r"^http://lib\.ru/(koi/|win/|lat/)?(.+\.txt)(_.*$)?"
            if not re.match(regex, link, flags=re.IGNORECASE):
                return render_response(request, "epub/get_book_from_libru.html", 
                                       {'errors': ['Not valid lib.ru path'], 
                                        'menu_on': True})
            match = re.search(regex, link, flags=re.IGNORECASE)
            search_link = match.group(2)
            
            books = Book.objects.filter(book_file__link__contains=search_link)

            if books:
                http = "http://lib.ru/" + search_link + "_with-big-pictures.html"
                book = books[0]
                name = book.title
                language = book.language
                authors = {}
                author_name = ""
                genres = []
                for i, author in enumerate(book.author.get_query_set()):
                    if i == 0:
                        author_name = author.name
                    else:
                        authors.append(author.name)
                for tag in book.tag.get_query_set():
                    genres.append(tag.name)
                temp_name = tempfile.mkstemp()
                properties = BookProperties(temp_name[1], name)
                print temp_name[1] + "  creation"
                properties.language = language
                properties.author = author_name
                properties.authors = authors
                properties.genre = ", ".join(genres)
                lrp = LibRuParser(http, properties)

                lrp.parse()
                if not lrp.create_book():
                    print "Error in creating book."

                folder = 'libru'
                link_name = settings.EPUB_URL + "/%s/%s/" % (settings.MEDIA_DOWNLOAD_FOLDER, folder) + quote(name.encode('utf-8')) + ".epub"
                book_folder = os.path.join(settings.MEDIA_ROOT,settings.MEDIA_DOWNLOAD_FOLDER, folder)
                if not os.path.exists(book_folder):
                    os.makedirs(book_folder)
                book_name = os.path.join(book_folder, name.encode("utf-8") + ".epub")
                shutil.copy(temp_name[1], book_name)
                os.chmod(book_name, 0666)
                return HttpResponseRedirect("/" + link_name)
            else:
                return render_response(request, "epub/get_book_from_libru.html", 
                                       {'messages': ["Sorry, but this book cannot be imported"], 'menu_on': True})

    else:
        return render_response(request, "epub/get_book_from_libru.html", {'user': request.user, 'menu_on': True})

def my_404_view(request):
    return render_response(request, "404.html", {'user': request.user})


def ajax(request):
    empty = False
    if 'letter' in request.GET and request.GET['letter']:
        if 'page' in request.GET:
            page = int(request.GET['page']) - 1
        else:
            page = 0
        authors = Author.objects.filter(name__istartswith=
                                        request.GET['letter'])
#        num = len(authors)
#        if len(authors) - page * RESULTS_PER_PAGE - 1 > RESULTS_PER_PAGE:
#            authors = authors[page * RESULTS_PER_PAGE:(page + 1) *
#                                                  RESULTS_PER_PAGE]
#        else:
#            authors = authors[page * RESULTS_PER_PAGE:]
    else:
        empty = True
        authors = []

    return render_response(request, "ajax/authors.xml", {'authors': authors, 'empty': empty})
