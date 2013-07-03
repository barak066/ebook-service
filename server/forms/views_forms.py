from django import forms
from django.utils.translation import ugettext as _

from forms.autocomplete_widget import AutocompleteWidget

from book.models import Book, Language, Tag
from book.widgets import LanguageWidget

def available_languages(site):
    '''returns all languages used in books in our data base'''
    all_langs = Language.objects.all().exclude(book__isnull=True)
    langs = []
    if not site == "libru":
        langs = Language.objects.all().exclude(book__isnull=True)
        return langs
    for lang in all_langs:
        books = lang.book_set.filter(pagelink__startswith="http://lib.ru")
        if books:
            langs.append(lang)
    return langs

def get_language_choices():
    temp = []
    for lang in Language.objects.all():
        temp.append((lang.short, lang.full,))

    return temp

class ExtendedSearch(forms.Form):
    title = forms.CharField(label=_('Title'),
        widget=AutocompleteWidget(choices_url='autocomplete_title', 
                                                related_fields=('author',)))

    author = forms.CharField(label=_('Author'),
        widget=AutocompleteWidget(choices_url='autocomplete_author', 
                                                    related_fields=('title',)))
    
    language = forms.CharField(widget=LanguageWidget(choices=available_languages("")))
    
    tags = forms.CharField(widget=forms.Select(choices=Tag.objects.all().order_by("name")))

class DocCreateForm(forms.Form):
    title = forms.CharField(label=_('Title') + '*')

    language = forms.CharField(label=_('Language') + '*', max_length=3,
                widget=forms.Select(choices=get_language_choices()))

    subject = forms.CharField(label=_('Subject'), required=False)

    description = forms.CharField(widget=forms.widgets.Textarea(), 
                                  label=_('Description'), required=False)

    type = forms.CharField(label=_('Type'), required=False)

    date = forms.CharField(label=_('Date'), required=False)

    rights = forms.CharField(label=_('Rights'), required=False)

    file = forms.FileField(label=_('File') + '*')

class EpubAddForm(forms.Form):
    caption = forms.CharField(label=_('Title') + '*')

    language = forms.CharField(label=_('Language') + '*', max_length=3,
                widget=forms.Select(choices=get_language_choices()))

    file = forms.FileField(label=_('File') + '*')

    toc = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':4, 'cols':60}), 
                          label=_('Table of contents'), required=False)

    tags = forms.CharField(label=_('Tags'), required=False)

    subject = forms.CharField(label=_('Subject'), required=False)

    type = forms.CharField(label=_('Type'), required=False)

    date = forms.CharField(label=_('Date of publication'), required=False)

    rights = forms.CharField(label=_('Rights'), required=False)

    description = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':4, 'cols':60}),
                                  label=_('Description'), required=False)
