try:
    import xml.etree.ElementTree as etree
except ImportError:
    import elementtree.ElementTree as etree

try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

from django.test import TestCase
from django.db.models import Q

from book.models import *
from book.action_handler import *
from book.get_action import get_by_id, get_q, make_q_from_tag, get_authors_q, get_files_q

from book.insert_action import get_authors, get_files, get_book_inf, save_book_inf

from spec.exception import InputDataServerException

xml_string_insert_new = '''
<authors>
    <author>
        <name>Name</name>
        <alias> </alias>
        <alias> </alias>
    </author>
    <author>
        <name>  
        </name>
    </author>
    <author>
        <name>Name2 </name>
        <alias>Alias </alias>
    </author>
    <author>
        <name></name>
        <alias>Alias2</alias>
    </author>
    <author>
        <name>Name1</name>
        <alias>Alias6</alias>
        <alias>Alias7</alias>
        <alias>Alias8</alias>
    </author>
</authors>'''


class InsertActionTest(TestCase):
    
    def setUp(self):
        "Adds 'unknown' language"
        self.unknown_language = Language.objects.create(short='?', full='unknown')

    def test_get_authors_inser_new(self):
        xml = etree.fromstring(xml_string_insert_new)
        authors = (get_authors(xml))[0]
#        authors.order_by(id)

        author = authors[0]
        self.failUnlessEqual(author.name, 'Name')
        self.failUnlessEqual(author.alias.count(), 0)

        author = authors[1]
        self.failUnlessEqual(author.name, 'Name2')
        self.failUnlessEqual(author.alias.all()[0].name, 'Alias')
        self.failUnlessEqual(author.alias.count(), 1)

        author = authors[2]
        self.failUnlessEqual(author.name, 'Name1')
        self.failUnlessEqual(author.alias.all()[0].name, 'Alias6')
        self.failUnlessEqual(author.alias.all()[1].name, 'Alias7')
        self.failUnlessEqual(author.alias.all()[2].name, 'Alias8')
        self.failUnlessEqual(author.alias.count(), 3)


    def test_get_authors_update_exists(self):
        xml = etree.fromstring(xml_string_insert_new)
        authors = get_authors(xml)
        xml_string = '''
        <authors>
            <author>
                <name>Name</name>
                <alias>Alias</alias>
            </author>
            <author>
                <name>  
                </name>
            </author>
            <author>
                <name>Name2</name>
                <alias>Alias </alias>
            </author>
            <author>
                <name></name>
                <alias>Alias2</alias>
            </author>
            <author>
                <name>Name1 </name>
                <alias>Alias6</alias>
                <alias>Alias7</alias>
                <alias>Alias9</alias>
            </author>
        </authors>'''
        
        xml = etree.fromstring(xml_string)
        authors = get_authors(xml)

        author = Author.objects.get(name='Name')
        alias = AuthorAlias.objects.get(name='Alias')
        self.failUnlessEqual(author.alias.all()[0].id, alias.id)

        author = Author.objects.get(name='Name1')
        self.failUnlessEqual(author.alias.count(), 4)
        self.failUnlessEqual(author.alias.all()[3].name, 'Alias9')


    def test_get_files_insert_new(self):
        "Tests insert new fiels"
        xml_string = '''
       <files>
        <file>
            <link> http://link  </link>
            <size></size>
            <type></type>
            <time_found></time_found>
            <last_check></last_check>

            <more_info></more_info>
            <img_link></img_link>
        </file>
       </files>
''';
        xml = etree.fromstring(xml_string)
        files = get_files(xml)

        file = BookFile.objects.get(link='http://link')
        self.failUnlessEqual(BookFile.objects.all()[0].id, file.id)
        self.failUnlessEqual(0, file.size)

    def test_get_files_check_size(self):
        "Tests checking size field"
        xml_string = '''
       <files>
        <file>
            <link> http://link  </link>
            <size>wrong</size>
        </file>
        <file>
            <link> http://link1  </link>
            <size>645</size>
        </file>
       </files>
''';
        xml = etree.fromstring(xml_string)
        files = get_files(xml)
        self.failUnlessEqual(BookFile.objects.all()[0].size, 0)
        self.failUnlessEqual(BookFile.objects.all()[1].size, 645)

    def test_get_files_check_empty(self):
        "Tests empty file if link is empty"
        xml_string = '''
       <files>
        <file>
            <link> </link>
            <size>84</size>
        </file>
       </files>
''';
        xml = etree.fromstring(xml_string)
        files = get_files(xml)
        self.failUnlessEqual(BookFile.objects.all().count(), 0)


    def test_get_book_inf_raise_except(self):
        "Tests raising InputDataServerException exception"
        xml_string = '''
        <book>
            <title>
            </title>
            <file>
              <link>link</link>
            </file>
        </book>
        ''';
        xml = etree.fromstring(xml_string)
        self.assertRaises(InputDataServerException, get_book_inf, xml)

    def test_book_inf(self):
        "Tests getting book inf"
        xml_string = '''
        <book>
            <title>Book title   </title>
            <lang>en</lang>
            <files>
              <file>
                <link>link</link>
              </file>
            </files>
        </book>
        ''';
        xml = etree.fromstring(xml_string)
        (book, authors, book_files, annotations) = get_book_inf(xml)
        self.failUnlessEqual(book.title, 'Book title')
        self.failUnlessEqual(book.language, self.unknown_language)

    def test_book_inf_authors(self):
        "Tests getting book authors"
        Author(name='Name').save()
        xml_string = '''
        <book>
            <title>Book title   </title>
            <authors>
                <author>
                    <name>Name2</name>
                    <alias>Alias</alias>
                </author>
                <author>
                    <name>Name</name>
                    <alias>Alias</alias>
                </author>
                <author>
                    <name>  
                    </name>
                </author>
            </authors>
            <files>
              <file>
                <link>link</link>
              </file>
            </files>
        </book>
        ''';
        xml = etree.fromstring(xml_string)
        (book, authors, book_files, annotations) = get_book_inf(xml)
        self.failUnlessEqual(authors[0], Author.objects.all()[1])
        self.failUnlessEqual(authors[1], Author.objects.all()[0])
        self.failUnlessEqual(Author.objects.all().count(), 2)

    def test_book_inf_files(self):
        "Tests getting book_files"
        link_hash = md5('link').hexdigest()
        BookFile(link='link', link_hash=link_hash).save()
        xml_string = '''
        <book>
            <title>Book title   </title>
            <files>
            <file>
                <link>link  </link>
                <size>wrong</size>
            </file>
            <file>
            <link>link2</link>
            <size>645</size>
            </file>
        </files>
        </book>
        ''';
        xml = etree.fromstring(xml_string)
        (book, authors, book_files, annotations) = get_book_inf(xml)
        self.failUnlessEqual(book_files[0], BookFile.objects.all()[0])
        self.failUnlessEqual(book_files[1], BookFile.objects.all()[1])
        self.failUnlessEqual(BookFile.objects.all().count(), 2)
        

    def test_save_book_info_book(self):
        'Tests creating and updating book'
        book = Book(title='title', lang='en')
        save_book_inf(book, [], [], [])
        self.failUnlessEqual(Book.objects.all()[0].title, 'title')
        self.failUnlessEqual(Book.objects.all()[0].lang, 'en')
        self.failUnlessEqual(Book.objects.all().count(), 1)

        # test update lang
        book = Book(title='title2', lang='', language=self.unknown_language)
        book.save()
        book.lang = 'fr'
        save_book_inf(book, [], [], [])
        self.failUnlessEqual(Book.objects.all()[1].title, 'title2')
        self.failUnlessEqual(Book.objects.all()[1].lang, 'fr')
        self.failUnlessEqual(Book.objects.all().count(), 2)

    def test_save_book_info_add_author(self):
        'tests adding authors to book'
        book = Book(title='title', lang='en')
        Author(name='auhtor name').save()
        Author(name='auhtor name2').save()
        save_book_inf(book, Author.objects.all(), [], [])
        
        self.failUnlessEqual(Author.objects.all().count(), 2)
        self.failUnlessEqual(Book.objects.all()[0].author.all().count(), 2)
        self.failUnlessEqual(Author.objects.all()[0], Book.objects.all()[0].author.all()[0])
        self.failUnlessEqual(Author.objects.all()[1], Book.objects.all()[0].author.all()[1])

        book = Book(title='title', lang='')
        author3 = Author(name='auhtor name3')
        author3.save()
        save_book_inf(book, Author.objects.all(), [], [])
        
        self.failUnlessEqual(Author.objects.all().count(), 3)
        self.failUnlessEqual(Book.objects.all()[1].author.all().count(), 3)
        self.failUnlessEqual(Author.objects.all()[0], Book.objects.all()[1].author.all()[0])
        self.failUnlessEqual(Author.objects.all()[1], Book.objects.all()[1].author.all()[1])
        self.failUnlessEqual(Author.objects.all()[2], Book.objects.all()[1].author.all()[2])

    def test_save_book_info_add_files(self):
        'tests adding book_files to book'
        book = Book(title='title', lang='en')
        book_file = BookFile(link='link', link_hash=md5('link').hexdigest())
        book_file.save()

        # set book_file to unexisting book
        save_book_inf(book, [], [book_file], [])

        self.failUnlessEqual(Book.objects.all()[0].book_file.all().count(), 1)
        self.failUnlessEqual(Book.objects.all()[0].book_file.all()[0], book_file)

        book_file2 = BookFile(link='link2', link_hash=md5('link2').hexdigest())
        book_file2.save()

        # add book_file to existing book
        save_book_inf(book, [], [book_file2, book_file], [])

        self.failUnlessEqual(Book.objects.all()[0].book_file.all().count(), 2)
        self.failUnlessEqual(Book.objects.all()[0].book_file.all()[1], book_file2)

