"Views for analyzer"
# -*- coding: utf-8 -*-

try:
    import xml.etree.ElementTree as etree
except ImportError:
    import elementtree.ElementTree as etree
import logging
from xml.parsers.expat import ExpatError
from sys import exc_info

from django.shortcuts import render_to_response
from django.template import Context

from settings import EBST_NAME, EBST_VERSION, EBST_VERSION_BUILD
try:
    from settings import ANALYZER_DEBUG_MODE
except ImportError:
    ANALYZER_DEBUG_MODE = False

from spec.exception import RequestFileServerException, \
ServerException, InnerServerException
from book.search import xml_search
from book.data_modify import exec_update
from book.request_check import check_ip, get_xml_request


MAIN_LOG = logging.getLogger("main_logger")
ANALYSER_LOG = logging.getLogger("analyser_logger")


def who(request):
    '''Generates default page'''
    context = Context({'name': EBST_NAME,
                       'version': EBST_VERSION,
                       'build': EBST_VERSION_BUILD})
    return render_to_response('data/default.xml', context)


def analyzer_view(request, action):
    "View for analyser interface"
    try:

        messages = []

        check_ip(request)
        xml_request = get_xml_request(request)

        # parse request
        try:
            xml = etree.fromstring(xml_request.encode('utf-8'))
        except ExpatError, ex:
            raise RequestFileServerException(ex.message)

        if action == 'SEARCH':
            # execute search request
            (entity_type, entities) = xml_search(xml)
            return render_to_response('data/search.xml', \
                                      Context({entity_type: entities,}))
        else:
            exec_update(xml)

    except InnerServerException, ex:
        exception_type, exception_value, exception_traceback = exc_info()
        msg_body = "%s: %s" % (exception_type, exception_value)
        messages.append(('error', msg_body))
        MAIN_LOG.exception(ex)

    except ServerException:
        exception_type, exception_value, exception_traceback = exc_info()
        msg_body = "%s: %s" % (exception_type, exception_value)
        messages.append(('error', msg_body))
        ANALYSER_LOG.warning(msg_body)

    except Exception, ex:
        exception_type, exception_value, exception_traceback = exc_info()
        msg_body = "%s: %s" % (exception_type, exception_value)
        MAIN_LOG.exception(ex)
        if not ANALYZER_DEBUG_MODE:
            messages.append(('error', msg_body))
        else:
            raise
        
        
    # computation of operation status 
    msg_types = (msg_type for msg_type, msg in messages)
    if 'error' in msg_types:
        status = 'error'
    elif 'warning' in msg_types:
        status = 'warning'
    else:
        status = 'ok'

    # load all vars to context
    context_dict = {
        'status': status,
        'messages': messages,
    }

    return render_to_response('data/main_response.xml', Context(context_dict))

#def data_modify(request, action):
#    '''Gets inf from POST, sends to action handler, builds response'''
#    context_dict = {}
#    messages = []
#
#    MAIN_LOG.info("Got connection from analyzer")
#    messages.append(('debug', 'Starting'))
#
#    try:
#
#        check_ip(request)
#        xml_request = get_xml_request(request)
#
#        # parse request
#        try:
#            xml = etree.fromstring(xml_request.encode('utf-8'))
#        except ExpatError, ex:
#            raise RequestFileServerException(ex.message)
#
#        # execute request
#        if action == ACTION['get']:
#            books = xml_exec_get(xml)
#            return render_to_response('data/analyser_response.xml', \
#                                      {'books': books, 'status': 'ok',})
#        elif action == ACTION['insert']:
#            messages = xml_exec_insert(xml)
#        else:
#            raise InnerServerException("Unknow action")
#
#    except InnerServerException, ex:
#        exception_type, exception_value, exception_traceback = exc_info()
#        msg_body = "%s: %s" % (exception_type, exception_value)
#        messages.append(('error', msg_body))
#        MAIN_LOG.exception(ex)
#
#    except ServerException:
#        exception_type, exception_value, exception_traceback = exc_info()
#        msg_body = "%s: %s" % (exception_type, exception_value)
#        messages.append(('error', msg_body))
#        MAIN_LOG.warning(msg_body)
#
#    except Exception, ex:
#        if not ANALYZER_DEBUG_MODE:
#            exception_type, exception_value, exception_traceback = exc_info()
#            msg_body = "%s: %s" % (exception_type, exception_value)
#            messages.append(('error', msg_body))
#            MAIN_LOG.exception(ex)
#        else:
#            raise
#        
#        
#    # computation of operation status 
#    msg_types = (msg_type for msg_type, msg in messages)
#    if 'error' in msg_types:
#        status = 'error'
#    elif 'warning' in msg_types:
#        status = 'warning'
#    else:
#        status = 'ok'
#
#    # load all vars to context
#    context_dict = {
#        'status': status,
#        'messages': messages,}
#
#    return render_to_response('data/main_response.xml', Context(context_dict))
