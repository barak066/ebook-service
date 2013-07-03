'''Module register our functions to use in template'''
# -*- coding: utf-8 -*-

from django.template import get_library
from django.contrib.admin.templatetags.admin_list import result_headers
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_unicode, force_unicode
from django.utils.safestring import mark_safe
from django.utils.html import escape, conditional_escape
from django.contrib.admin.templatetags.admin_list import _boolean_icon
from django.contrib.admin.views.main import EMPTY_CHANGELIST_VALUE
from django.utils.translation import get_date_formats
from django.utils.text import capfirst
from django.utils import dateformat
from django import template

from book.models import Author

#REGISTER = get_library('django.templatetags.admin_list')

register = template.Library()

def my_items_for_result(cl, result, form):
    ''' 
    defines onclick function in book's change_list 
    (returns _unicode_() instead of id )
    '''
    first = True
    cl_pk = cl.lookup_opts.pk.attname
    for field_name in cl.list_display:
        row_class = ''
        try:
            field = cl.lookup_opts.get_field(field_name)
        except models.FieldDoesNotExist:
            try:
                if callable(field_name):
                    attr = field_name
                    value = attr(result)
                elif hasattr(cl.model_admin, field_name) and \
                   not field_name == '__str__' and not field_name == '__unicode__':
                    attr = getattr(cl.model_admin, field_name)
                    value = attr(result)
                else:
                    attr = getattr(result, field_name)
                    if callable(attr):
                        value = attr()
                    else:
                        value = attr
                allow_tags = getattr(attr, 'allow_tags', False)
                boolean = getattr(attr, 'boolean', False)
                if boolean:
                    allow_tags = True
                    result_repr = _boolean_icon(value)
                else:
                    result_repr = smart_unicode(value)
            except (AttributeError, ObjectDoesNotExist):
                result_repr = EMPTY_CHANGELIST_VALUE
            else:
                if not allow_tags:
                    result_repr = escape(result_repr)
                else:
                    result_repr = mark_safe(result_repr)
        else:
            field_val = getattr(result, field.attname)

            if isinstance(field.rel, models.ManyToOneRel):
                if field_val is not None:
                    result_repr = escape(getattr(result, field.name))
                else:
                    result_repr = EMPTY_CHANGELIST_VALUE
            elif isinstance(field, models.DateField) or isinstance(field, models.TimeField):
                if field_val:
                    (date_format, datetime_format, time_format) = get_date_formats()
                    if isinstance(field, models.DateTimeField):
                        result_repr = capfirst(dateformat.format(field_val, datetime_format))
                    elif isinstance(field, models.TimeField):
                        result_repr = capfirst(dateformat.time_format(field_val, time_format))
                    else:
                        result_repr = capfirst(dateformat.format(field_val, date_format))
                else:
                    result_repr = EMPTY_CHANGELIST_VALUE
                row_class = ' class="nowrap"'
            elif isinstance(field, models.BooleanField) or isinstance(field, models.NullBooleanField):
                result_repr = _boolean_icon(field_val)
            elif isinstance(field, models.DecimalField):
                if field_val is not None:
                    result_repr = ('%%.%sf' % field.decimal_places) % field_val
                else:
                    result_repr = EMPTY_CHANGELIST_VALUE
            elif field.flatchoices:
                result_repr = dict(field.flatchoices).get(field_val, EMPTY_CHANGELIST_VALUE)
            else:
                result_repr = escape(field_val)
        if force_unicode(result_repr) == '':
            result_repr = mark_safe('&nbsp;')
        if (first and not cl.list_display_links) or field_name in cl.list_display_links:
            table_tag = {True:'th', False:'td'}[first]
            first = False
            url = cl.url_for_result(result)
            if cl.to_field:
                attr = str(cl.to_field)
            else:
                attr = cl_pk
            value = result.serializable_value(attr)
            result_id = repr(force_unicode(value))[1:]

            ######### my representation for books in author
            if isinstance(result, Author):
                result_name = repr(force_unicode(result.name))[1:]

                yield mark_safe(u'<%s%s><a href="%s"%s>%s</a></%s>' % \
                    (table_tag, row_class, url, (cl.is_popup and ' onclick="opener.checkboxDismissRelatedLookupPopup(window, %s, %s); return false;"' %(result_id, result_name) or ('','')), conditional_escape(result_repr), table_tag))
            else:
                yield mark_safe(u'<%s%s><a href="%s"%s>%s</a></%s>' % \
                    (table_tag, row_class, url, (cl.is_popup and ' onclick="opener.checkboxDismissRelatedLookupPopup(window, %s); return false;"' %result_id or ''), conditional_escape(result_repr), table_tag))
        else:
            if form and field_name in form.fields:
                form_field_name = form[field_name]
                result_repr = mark_safe(force_unicode(form_field_name.errors) + force_unicode(form_field_name))
            else:
                result_repr = conditional_escape(result_repr)
            yield mark_safe(u'<td%s>%s</td>' % (row_class, result_repr))
    if form:
        yield mark_safe(force_unicode(form[cl.model._meta.pk.name]))

def my_results(cl):
    ''' makes result list using my_items_for_result'''
    if cl.formset:
        for res, form in zip(cl.result_list, cl.formset.forms):
            yield list(my_items_for_result(cl, res, form))
    else:
        for res in cl.result_list:
            yield list(my_items_for_result(cl, res, None))

@register.inclusion_tag("admin/change_list_results.html")
def my_result_list(cl):
    '''returns context using my_results'''
    return {'cl': cl,
            'result_headers': list(result_headers(cl)),
            'results': list(my_results(cl))}

#my_result_list = REGISTER.inclusion_tag("admin/change_list_results.html")(my_result_list)

