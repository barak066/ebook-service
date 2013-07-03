
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

from django.db import IntegrityError
from django.db import transaction

from spec.exception import InputDataServerException
from book.models import Author, Book, BookFile, Language

from update_entity import update_author, update_book_file, update_book


def define_entity(xml):
    "Creates entity, returns dictionary with mapping from 'ui' to 'id'."

    # Mapping from 'ui' to 'id'
    ui_dic = {}

    try:
        for node in xml.getchildren():
    
            # Get 'ui' from tag attribute
            entity_ui = int(node.attrib['ui'])
            # Check 'ui' uniqueness
            if entity_ui in ui_dic:
                raise InputDataServerException("For '%s' ui=%s is not unique" %
                                               (node.tag, entity_ui))
        
            # Create entity
            if node.tag == 'author':
                entity_id = update_author(node).id
            elif node.tag == 'file':
                entity_id = update_book_file(node).id
            elif node.tag == 'book':
                entity_id = update_book(node).id
            else:
                raise InputDataServerException(
                        "Unexpected tag '%s' in define section" % node.tag)
            ui_dic[entity_ui] = entity_id
    
    except IntegrityError, ex:
        raise InputDataServerException(ex)
    except KeyError:
        raise InputDataServerException("One entity dosn't have 'ui' attrubute")
    except ValueError:
        raise InputDataServerException("'ui' has to be integer.")

    return ui_dic


def update_entity(xml, ui_dic):

    # Replace all 'ui' to 'id'
    try:
        for node in xml.getiterator():
            if 'ui' in node.attrib:
                node.set('id', ui_dic[int(node.attrib['ui'])] )
    except ValueError:
        raise InputDataServerException("'ui' have to be integer.")
    except KeyError:
        raise InputDataServerException("Using undefined 'ui'.")

    for node in xml.getchildren():
        # Check 'id'
        if not node.attrib.get('id'):
            raise InputDataServerException(
                    "'%s' in update section doesn't have 'id' or 'ui'." %
                    node.tag)
        if node.tag == 'author':
            update_author(node)
        elif node.tag == 'file':
            update_book_file(node)
        elif node.tag == 'book':
            update_book(node)
        else:
            raise InputDataServerException(
                    "Unexpected tag '%s' in define section" % node.tag)


@transaction.commit_manually
def exec_update(xml):
    
    define_xml = xml.find('define')
    update_xml = xml.find('update')

    if not update_xml:
        raise InputDataServerException("Not found tag 'update'")
        
    try:
        ui_dict = {}
        if define_xml:
            # Create entities from define section
            ui_dict = define_entity(define_xml)
        # Update entities
        update_entity(update_xml, ui_dict)
    except:
        transaction.rollback()
        raise

    transaction.commit()

