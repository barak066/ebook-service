
try:
    import xml.etree.ElementTree as etree
except ImportError:
    import elementtree.ElementTree as etree

try:
    from hashlib import md5
except ImportError:
    import md5

from django.test import TestCase
from django.db.models import Q

from book.models import *

from spec.exception import InputDataServerException

from book.data_modify import define_entity, update_entity, exec_update

XML_STRING = """
<request>
    <define>
        <author ui="1"> <full_name> author1 </full_name> </author>
        <author ui="2"> <full_name> author2 </full_name> </author>

        <file ui="3"> <link> link3 </link> </file>
        <file ui="4"> <link> link4 </link> </file>

        <book ui="5"> <title> title1 </title> </book>
    </define>

    <update>
        <book ui="5">
            <authors>
                <author ui="1" />
                <author ui="2" />
            </authors>
            <files>
                <file ui="3" />
                <file ui="4" />
            </files>
        </book>
    </update>
</request>
"""

STR_UPDATE_AUTHOR = """
<request>
    <update>
        <author id="1"> <full_name> other</full_name> </author>
    </update>
</request>
"""


class DefineEntityTest(TestCase):

    def setUp(self):
        self.xml = etree.fromstring(XML_STRING)
        

    def test_entity_ui(self):
        xml_string = """
        <define>
        <author>
        </author>
        </define>
        """
        xml = etree.fromstring(xml_string)
        self.assertRaises(InputDataServerException, define_entity, xml)

        xml_string = """
        <define>
        <author ui="2" />
        <author ui="3" />
        <author ui="5" />
        <author ui="2" />
        </define>
        """
        xml = etree.fromstring(xml_string)
        self.assertRaises(InputDataServerException, define_entity, xml)
        
    
    def test_add_author(self):
        xml_string = """
        <define>
        <author ui='3'>
            <full_name>Tipa</full_name>
        </author>
        </define>
        """
        xml = etree.fromstring(xml_string)
        define_entity(xml)

class ExecUpdateTest(TestCase):
    
    def setUp(self):
        self.xml = etree.fromstring(XML_STRING)
        self.xml_update_author = etree.fromstring(STR_UPDATE_AUTHOR)
        Language(short='?').save()

    def test_update_absence(self):
        self.xml.find('update').clear()
        self.assertRaises(InputDataServerException, exec_update, self.xml)

    def test_all(self):
        exec_update(self.xml)
        b = Book.objects.get(title="title1")
        self.failUnless(set(b.author.all()), \
                        set(Author.objects.all()))

        self.failUnless(set(b.book_file.all()), \
                        set(BookFile.objects.all()))

        self.failUnless(set(Author.objects.values_list('name', flat=True)), \
                        set(['author1', 'author2']))

        self.failUnless(set(BookFile.objects.values_list('link', flat=True)), \
                        set(['link3', 'link4']))


    def test_update_author(self):
        Author(id=1, name='name').save()
        exec_update(self.xml_update_author)
        self.failUnless(Author.objects.get(id=1).name, 'other')

