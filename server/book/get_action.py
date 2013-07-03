'''Action handler of get request;'''

from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from spec.exception import InputDataServerException
from book.models import Book


def get_q(object_name, arg, search_type=''):
    "Makes Q object for 'object_name' with search type from 'search_type' \
    sets 'arg' like argument"
    if search_type:
        object_name = object_name + '__' + search_type
    q_obj = Q()
    q_obj.add((object_name, arg), 'AND')
    return q_obj


def get_by_id(entirety, node):
    "Trys to get entirety by id in attribute; Returns None if id is not defined"
    try:
        # gets id from attribute
        obj_id = node.attrib['id']
        return entirety.objects.get(id=obj_id)
    except ValueError:
        raise InputDataServerException("The %s id must be int" 
                                       % (entirety.__name__))
    except ObjectDoesNotExist:
        raise InputDataServerException(
              "The %s with id = %s does not exist in database"
              % (entirety.__name__, obj_id))
    except KeyError:
        pass
    return None


def make_q_from_tag(node, object_name, default_search_type=''):
    '''Makes Q objects for tag'''
    obj_id = node.get('id', 0)
    # if tag has attribute 'id'
    if obj_id:
        search_type = ''
        arg_search = obj_id
        object_name = object_name + '__id'
    else:
        search_type = node.get('type', default_search_type)
        arg_search = ''
        if node.text:
            arg_search = node.text.strip()
    return get_q(object_name, arg_search, search_type)


def get_authors_q(node):
    '''Makes Q object for authors in node'''
    q_obj = Q()
    for author_node in node.getchildren():
        if author_node.get('id', 0):
            q_obj = q_obj & make_q_from_tag(author_node, 'author')
        else:
            q_obj = q_obj & make_q_from_tag(author_node, 'author__name',
                                            'icontains')
    return q_obj


def get_files_q(node):
    '''Makes Q object for files in node'''
    q_obj = Q()
    for file_node in node.getchildren():
        if file_node.get('id', 0):
            q_obj = q_obj & Q(book_file__id=file_node.get('id'))
        else:
            # if not Q by id
            for det_node in file_node.getchildren():
                if det_node.tag == 'link':
                    q_obj = q_obj \
                          & make_q_from_tag(det_node, 'book_file__link', '')
                
                if det_node.tag == 'size':
                    q_obj = q_obj \
                          & make_q_from_tag(det_node, 'book_file__size', '')

    return q_obj



def xml_exec_get(xml):
    '''Makes QuerySet for Book from xml request
    Returns QuerySet'''

    # if they are book id, return it
    book = get_by_id(Book, xml)
    if book:
        return [book]

    q_obj = Q()
    
    # for by all tags in <book>
    for node in xml.getchildren():
        # if we found the tag 'title', add qeuryset to q
        if node.tag == 'title':
            q_obj = q_obj & make_q_from_tag(node, 'title', 'icontains')
                
        # if we found the tag 'lang', add qeuryset to q
        elif node.tag == 'lang':
            q_obj = q_obj & make_q_from_tag(node, 'lang')

        # if we found the tag 'annotation', add qeuryset to q
        elif node.tag == 'annotation':
            q_obj = q_obj & make_q_from_tag(node, 'annotation__name',
                                            'icontains')
            

        # if we found the tag 'authors', add qeuryset to q
        elif node.tag == 'authors':
            q_obj = q_obj & get_authors_q(node)

        # if we found the tag 'files', add qeuryset to q
        elif node.tag == 'files':
            q_obj = q_obj & get_files_q(node)
    
    return Book.objects.filter(q_obj)



#def get_author_queryset(xml):
#    '''Makes Q object for Author from xml request
#    Returns Q object'''
#
#    q_obj = Q()
#
#    # for each author
#    for node in xml.getchildren():
#        author = get_by_id(Author, node)
#        if author:
#            q_obj = q_obj & Q(author__id=author.id)
#        else:
#            name = replace_delim_to_space(node.text)
#            q_obj = q_obj & Q(author__name__icontains=name)
#
#    return q
#
#
#def get_file_queryset(xml):
#    '''Makes QuerySet for File from xml request
#    Returns QuerySet'''
#
#    q_obj = Q()
#
#    # for each file
#    for node in xml.getchildren():
#        file = get_by_id(BookFile, node)
#        if file:
#            q_obj = q_obj & Q(book_file__id=file.id)
#        else:
#            for file_det_node in node.getchildren():
#                if file_det_node.tag == 'link':
#                    link = replace_delim_to_space(file_det_node.text)
#                    q_obj = q_obj & Q(book_file__link=link)
#                elif file_det_node.tag == 'size':
#                    size = replace_delim_to_space(file_det_node.text)
#                    q_obj = q_obj & Q(book_file__size=size)
#                elif file_det_node.tag == 'type':
#                    type = replace_delim_to_space(file_det_node.text)
#                    q_obj = q_obj & Q(book_file__type=type)
#
#                # insert code for last_check and time_found
#
#                elif file_det_node.tag == 'more_info':
#                    more_info = file_det_node.text.strip()
#                    q_obj = q_obj 
#& Q(book_file__more_info__icontains=more_info)
#
#                # insert code for link_img
#
#
#
#def get_book_queryset(xml):
#    '''Makes QuerySet for Book from xml request
#    Returns QuerySet'''
#
#    # if they are book id, return it
#    book = get_by_id(Book, xml)
#    if book:
#        return [book]
#
#    q_obj = Q()
#    
#    # for by all tags in <book>
#    for node in xml.getchildren():
#        # if we found the tag 'title', add qeuryset to q
#        if node.tag == 'title':
#            title = replace_delim_to_space(node.text)
#            q_obj = q_obj & Q(title__icontains=title)
#                
#        # if we found the tag 'tag', add qeuryset to q
#        elif node.tag == 'lang':
#            lang = replace_delim_to_space(node.text)
#            q_obj = q_obj & Q(lang=lang)
#
#        # if we found the tag 'annotation', add qeuryset to q
#        elif node.tag == 'annotation':
#            annotation = get_by_id(Annotation, node)
#            if annotation:
#                q_obj = q_obj & Q(annotation=annotation)
#            else:
#                q_obj = q_obj & Q(annotation__name__icontains=node.text)
#
#
#        # if we found the tag 'authors', add qeuryset to q
#        elif node.tag == 'authors':
#            q_obj = q_obj & get_author_queryset(node)
#
#        # if we found the tag 'files', add qeuryset to q
#        elif node.tag == 'files':
#            q_obj = q_obj & get_file_queryset(node)
#
#
#
#    
