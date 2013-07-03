"SearchEngine interface implementation using Sphinx"

from UserList import UserList

from settings import MAX_RESULT_LENGTH
from book.search_engine.engine import SearchEngine
from book.search_engine.spell_checker import spell_check
from book.models import Author, Book, Language, Tag

MIN_LEN_RESULT = 5

class SphinxSearchEngine(SearchEngine):
    "Search engine using sphinx search."

    def __get_suggetions(self, **kwargs):
        lang = kwargs.get('lang')
        spelling_field = ['query', 'title', 'author']
        suggestions = dict([(key, spell_check(value, lang)) \
                            for key, value in kwargs.items() \
                            if key in spelling_field])
        suggestions = \
            dict([(key, value) for key, value in suggestions.items() \
                                              if value])
        if suggestions:
            return suggestions

    def __author_search(self, max_length, **kwargs):
        author_query = kwargs.get('author')
#        lang_query = kwargs.get('lang')
        tag_query = kwargs.get('tag')

        if author_query:
            authors = Author.simple_search.query(author_query)[0:5]
            authors_id = [a.id for a in authors]
            authors_soundex = Author.soundex_search.query(author_query)[0:max_length]
            for author in authors_soundex:
                if author.id not in authors_id:
                    authors.append(author)
#            if lang_query:
#                lang_id = Language.objects.get(short=lang_query).id
#                authors = authors.filter(language_id=lang_id)
#            if tag_query:
#                tag_id = Tag.objects.get(name=tag_query).id
#                authors = authors.filter(tag_id=tag_id)
            # TODO sort by normal weight

            return authors


    def author_search(self, max_length=MAX_RESULT_LENGTH, **kwargs):
        """
        Searchs query in authors, using soundex algorithm.
        Supports args: author, tag, max_length.
        """
        search_result = UserList(self.__author_search(max_length, **kwargs))
        if search_result is not None:
            search_result.suggestion = self.__get_suggetions(**kwargs)
            return search_result

    def __book_search(self, max_length, **kwargs):
        title_query = kwargs.get('title')
        author_query = kwargs.get('author')
        lang_query = kwargs.get('lang')
        tag_query = kwargs.get('tag')
        
        if title_query:
            books = Book.title_search.query(title_query)
            
            if lang_query:
                lang_id = Language.objects.get(short=lang_query).id
                books = books.filter(language_id=lang_id)

            if tag_query:
                tag_id = Tag.objects.get(name=tag_query).id
                books = books.filter(tag_id=tag_id)

            if author_query:
                authors = self.__author_search(author=author_query, \
                                               max_length=max_length)
                authors_id = [a.id for a in authors]
                if authors_id:
                    first_author_id = authors_id[0]
                    result_books = \
                        books._clone().filter(author_id=first_author_id)[0:max_length]

                    authors_id = authors_id[1:]
                    if authors_id:
                        additional_books = \
                            books.filter(author_id=authors_id)[0:max_length]
                        result_books.extend(additional_books)
                else:
                    result_books = books[0:max_length]

            else:
                result_books = books[0:max_length]

            return result_books
        

    def book_search(self, max_length=MAX_RESULT_LENGTH, **kwargs):
        """
        Searchs query in books.
        Supports args: title, author, tag, lang, max_length.
        """
        search_result = UserList(self.__book_search(max_length, **kwargs))
        if search_result is not None:
            search_result.suggestion = self.__get_suggetions(**kwargs)
            return search_result

    def simple_search(self, query, max_length=MAX_RESULT_LENGTH, **kwargs):
        """
        Smart searchs query in books (in title and authors).
        Supports args: query, tag, lang, max_length.
        """
        query_ex = dict(kwargs)
        query_ex['title'] = query
        query_ex['author'] = query

        # search in title and in author
        books = UserList(self.__book_search(max_length, **query_ex))
        
        if len(books) < max_length:
            # search only in title
            del query_ex['author']
            books_a = self.__book_search(max_length, **query_ex)

            books_id_set = set([b.id for b in books])
            # merge results
            added_book_num = len(books)
            for book in books_a:
                if not book.id in books_id_set:
                    books.append(book)
                    added_book_num += 1
                    if added_book_num == max_length:
                        break

        del query_ex['title']
        if len(books) < MIN_LEN_RESULT:
            query_ex['author'] = query
            authors = UserList(self.__author_search(1, **query_ex))
            if authors:
                # TODO add filtering by language and tag here
                authors_books = authors[0].book_set.all()
                books.extend(authors_books)
            del query_ex['author']

        query_ex['query'] = query
        books.suggestion = self.__get_suggetions(**query_ex)
        return books

