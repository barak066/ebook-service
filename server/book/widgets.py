'''Defines widgets for admin forms '''
# -*- coding: utf-8 -*-

from django import forms
from django.utils.encoding import force_unicode
from django.utils.html import escape, conditional_escape
from itertools import chain
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import ManyToManyRawIdWidget
from django.core.urlresolvers import reverse, NoReverseMatch

from book.models import Book, Author, Annotation, Language

class AuthorWidget(forms.CheckboxSelectMultiple, ManyToManyRawIdWidget):
    """
    A Widget for displaying ManyToMany authors(their names) in the "raw_id" 
    interface rather than in a <select multiple> box.
    """
    def __init__(self, rel, attrs=None):    
        super(AuthorWidget, self).__init__(attrs)
        self.rel = rel

    def render(self, name, value, attrs=None):
        ''' overloads base class method render'''
        attrs['class'] = 'vManyToManyRawIdAdminField'
        if value is None: value = []

        ################ our logic
        choices = list()        
        for v in value:
            choices.append((v, Author.objects.get(id=v).name))

        ##################

        if attrs is None:
            attrs = {}
        
        related_url = '../../../%s/%s/' % (self.rel.to._meta.app_label, 
                                        self.rel.to._meta.object_name.lower())
        params = self.url_parameters()
        if params:
            url = '?' + '&amp;'.join(['%s=%s' % (k, v) for k, v in params.items()])
        else:
            url = ''
        if not attrs.has_key('class'):
            attrs['class'] = 'vForeignKeyRawIdAdminField' 

        ############## our logic for view
        output = [forms.CheckboxSelectMultiple.render(self,name, value, attrs, choices)]

        ##############

        output.append('<a href="%s%s" class="related-lookup" id="lookup_id_%s" onclick="return showRelatedObjectLookupPopup(this);"> ' % \
            (related_url, url, name))
        output.append('<img src="%simg/admin/selector-search.gif" width="16" height="16" alt="%s" /></a>' 
                        % (settings.ADMIN_MEDIA_PREFIX, _('Lookup')))
        if value:
            output.append(self.label_for_value(value))
        return mark_safe(u''.join(output))

class LanguageWidget(forms.Select):
    """
    A Widget for displaying english, french, russian language in first place
    """

    def render_options(self, choices, selected_choices):
        ''' overloads base class method render_options'''
        def render_option(option_value, option_label, is_selected):
            ''' returns 'option' for each language in data base'''
            option_value = force_unicode(option_value)
            selected_html = (option_value in selected_choices) and u' selected="selected"' or ''
            if is_selected:
                selected_html = ''
            return u'<option value="%s"%s>%s</option>' % (
                escape(option_value), selected_html,
                conditional_escape(force_unicode(option_label)))
        # Normalize to strings.
        is_selected = False
        selected_choices = set([force_unicode(v) for v in selected_choices])
        output = []

        lang_id = str(Language.objects.get(short='ru').id)
        output.append(render_option(lang_id, 'Russian', is_selected))
        if lang_id in selected_choices:
            is_selected = True

        lang_id = str(Language.objects.get(short='en').id)
        output.append(render_option(lang_id, 'English', is_selected))
        if lang_id in selected_choices:
            is_selected = True
    
        lang_id = str(Language.objects.get(short='fr').id)
        output.append(render_option(lang_id, 'French', is_selected))
        if lang_id in selected_choices:
            is_selected = True

        output.append("<option disabled>------------</option>")

        for option_value, option_label in chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                output.append(u'<optgroup label="%s">' 
                                    % escape(force_unicode(option_value)))
                for option in option_label:
                    output.append(render_option(*option))
                output.append(u'</optgroup>')
            else:
                output.append(render_option(option_value, option_label, is_selected))
        return u'\n'.join(output)

class AnnotationWidget(forms.CheckboxSelectMultiple, ManyToManyRawIdWidget):
    """
    A Widget for displaying ManyToMany annotation in the "raw_id" 
    interface rather than in a <select multiple> box.
    """

    def __init__(self, rel, attrs=None):    
        super(AnnotationWidget, self).__init__(attrs)
        self.rel = rel

    def render_checkbox(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], option_value))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(u'<li><label%s >%s<a href="../../annotation/%s/" onclick="return showRelatedObjectLookupPopup(this);"> %s</a></label></li>' % (label_for, rendered_cb, option_value, option_label[0:100]+"..."))
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))

    def render(self, name, value, attrs=None):
        ''' overloads base class method render'''
        attrs['class'] = 'vManyToManyRawIdAdminField'
        if value is None: value = []
        ################ our logic
        choices = list()        
        for v in value:
            choices.append((v, Annotation.objects.get(id=v).name))

        ##################

        if attrs is None:
            attrs = {}
        
        related_url = '../../../%s/%s/' % (self.rel.to._meta.app_label, 
                                        self.rel.to._meta.object_name.lower())
        params = self.url_parameters()
        if params:
            url = '?' + '&amp;'.join(['%s=%s' % (k, v) for k, v in params.items()])
        else:
            url = ''


        ############## our logic for view
        output = [self.render_checkbox( name, value, attrs, choices)]

        ##############

        if value:
            output.append(self.label_for_value(value))
        output.append(u'<a href="%s" class="add-another" id="add_id_%s" onclick="return showAddAnotherPopup(this);"> ' % \
            (related_url, name))
        output.append(u'<img src="%simg/admin/icon_addlink.gif" width="10" height="10" alt="%s"/></a>' % (settings.ADMIN_MEDIA_PREFIX, _('Add Another')))
        return mark_safe(u''.join(output))

