from django.db import IntegrityError

from spec.exception import InputDataServerException
from spec.utils import get_language

from book.models import Author, Book, BookFile

def get_tag_text(xml, tag):
    "Finds 'tag' in 'xml', returns text content or None."
    node = xml.find(tag)
    if node is not None and node.text:
        text = node.text.strip()
        if not text:
            return None
        return text

def get_id(xml):
    """
    Tries to get 'id', if atribute doesn't exist, return None,
    else return 'id'
    """
    try:
        return int(xml.attrib['id'])
    except ValueError:
        raise InputDataServerException("'id' has to be integer.")
    except KeyError:
        return None


def update_author(xml):
    "Executes xml, creates author or updates inf about it."
    entity_id = get_id(xml)

    if entity_id is None:
        # Create new author
        author = Author()
    else:
        # Modify existing author
        author = Author.objects.get(id=entity_id)

    full_name = get_tag_text(xml, 'full_name')

    if full_name:
        author.name = full_name
    
    if not author.name:
        raise IntegrityError("'full_name' can't be empty")

    try:
        credit_str = get_tag_text(xml, 'credit')
        if credit_str:
            credit = int(credit_str)
            author.credit = credit
    except ValueError, ex:
        raise InputDataServerException(ex)

    author.save()

    return author
                

def update_book_file(xml):
    "Executes xml, creates book_file or updates inf about it."
    entity_id = get_id(xml)

    if entity_id:
        # Modify existing book_file
        book_file = BookFile.objects.get(id=entity_id)
    else:
        # Create new book_file
        book_file = BookFile()

    # TODO check necessary fileds
    link = get_tag_text(xml, 'link')
    file_type = get_tag_text(xml, 'type')
    more_info = get_tag_text(xml, 'more_info')
    img_link = get_tag_text(xml, 'img_link')

    try:
        size_str = get_tag_text(xml, 'size')
        if size_str:
            book_file.size = int(size_str)
        credit_str = get_tag_text(xml, 'credit')
        if credit_str:
            book_file.credit = int(credit_str)
    except ValueError, ex:
        raise InputDataServerException(ex)

    if link:
        book_file.link = link
    if not link:
        raise IntegrityError("'link' can't be empty")

    if file_type:
        book_file.type = file_type
    if more_info:
        book_file.more_info = more_info
    if img_link:
        book_file.img_link = img_link

    book_file.save()
    return book_file


def update_book(xml):
    "Executes xml, creates book or updates inf about it."
    entity_id = get_id(xml)
    now_created = False

    if entity_id:
        # Modify existing book
        book = Book.objects.get(id=entity_id)
    else:
        # Create new book
        book = Book()
        now_created = True

    title = get_tag_text(xml, 'title')
    lang = get_tag_text(xml, 'lang')

    lang = get_language(lang)

    try:
        credit_str = get_tag_text(xml, 'credit')
        if credit_str:
            book.credit = int(credit_str)
    except ValueError, ex:
        raise InputDataServerException(ex)

    if title:
        book.title = title
    if lang:
        book.language = lang

    if not book.title:
        raise IntegrityError("'title' can't be empty")

    book.save()

    def relation_process(xml, entity_object, entity_set, entity_str):
        rm_entities = None
        if xml:
            # Get id of all authors
            entities_id = \
                [int(entity.attrib['id']) for entity in xml.findall(entity_str)]
    
            if xml.attrib.get('reset') == entity_str:
                old_entities_id = set(entity_set.values_list('id', flat=True))
                rm_entities_id = old_entities_id.difference(entities_id)
                rm_entities = entity_object.objects.filer(id__in=rm_entities_id)
    
                entity_set.remove(rm_entities)
            
            [entity_set.add(entity_id) for entity_id in entities_id]
        return rm_entities

    rm_authors = relation_process(xml.find('authors'), Author, \
                                  book.author, 'author')
    # TODO check rm_authors for hide in result, if its don't have book

    rm_book_files = relation_process(xml.find('files'), BookFile, \
                                    book.book_file, 'file')
    # TODO check rm_book_files for hide in result, if its don't have book

    if not now_created:
        if not book.author.count():
            raise IntegrityError("'authors' can't be empty")
        if not book.book_file.count():
            raise IntegrityError("'files' can't be empty")

    return book
