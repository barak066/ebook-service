"Interface for search engine."

from settings import MAX_RESULT_LENGTH

class SearchEngine:
    """
    Abstract class, interface for search engine.
    Each method returns iterable collection
    with attribute 'suggestion', None if there are not suggestios or
    dict like {'author': 'Tolstoy', title: 'Anna Karenina'}
    """

    def author_search(self, max_length=MAX_RESULT_LENGTH, **kwargs):
        "Searchs query in authors."
        raise NotImplementedError(
            'SearchEngine.author_search() must be implemented in subclasses')

    def book_search(self, max_length=MAX_RESULT_LENGTH, **kwargs):
        "Searchs query in books."
        raise NotImplementedError(
            'SearchEngine.book_search() must be implemented in subclasses')

    def simple_search(self, query, max_length=MAX_RESULT_LENGTH, **kwargs):
        "Smart searchs query in books."
        raise NotImplementedError(
            'SearchEngine.simple_search() must be implemented in subclasses')
