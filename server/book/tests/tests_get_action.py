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

from book.tests.tests_insert_action import InsertActionTest

class GetActionTest(TestCase):

    def test_get_q(self):
        md5("sd").hexdigest()

        q = get_q('title', 'query', 'icontains')
        qm = Q(title__icontains='query')
        self.failUnlessEqual(q.__str__(), qm.__str__())

        q = get_q('file__size', 'query')
        qm = Q(file__size='query')
        self.failUnlessEqual(q.__str__(), qm.__str__())


    def test_make_q_from_tag(self):
        # simple test
        xml_string = '<tag> text</tag>'
        xml = etree.fromstring(xml_string)
        q = make_q_from_tag(xml, 'tag')

        qm = Q(tag='text')
        self.failUnlessEqual(q.__str__(), qm.__str__())

        # test with search type
        xml_string = '<tag type="gt"> text </tag>'
        xml = etree.fromstring(xml_string)
        q = make_q_from_tag(xml, 'tag__name')

        qm = Q(tag__name__gt='text')
        self.failUnlessEqual(q.__str__(), qm.__str__())

        # test with search type and several object
        xml_string = '<tag id="4"> text </tag>'
        xml = etree.fromstring(xml_string)
        q = make_q_from_tag(xml, 'tag')

        qm = Q(tag__id='4')
        self.failUnlessEqual(q.__str__(), qm.__str__())


    def test_get_authors_q(self):
        xml_string = '''
        <authors>
            <author>name</author>
            <author type=""> name2 </author>
            <author id="4">name3</author>
        </authors>'''

        xml = etree.fromstring(xml_string)
        q = get_authors_q(xml)

        qm = Q(author__name__icontains='name') \
           & Q(author__name='name2') \
           & Q(author__id='4')
        self.failUnlessEqual(q.__str__(), qm.__str__())

    def test_get_files_q(self):
        xml_string = '''
        <files>
            <file><link>  http://link.ruosd</link></file>
            <file>
                <link>http://link.rutosd</link>
                <size>986</size>
            </file>
            <file type="less"> <size type="less">45</size> </file>
            <file id="4">name3</file>
        </files>'''


        xml = etree.fromstring(xml_string)
        q = get_files_q(xml)

        qm = Q(book_file__link='http://link.ruosd') \
           & Q(book_file__link='http://link.rutosd') \
           & Q(book_file__size='986') \
           & Q(book_file__size__less='45') \
           & Q(book_file__id='4')
        self.failUnlessEqual(q.__str__(), qm.__str__())
