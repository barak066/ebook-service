'''Defines forms for admin view'''
# -*- coding: utf-8 -*-

from book.models import Author, Book, Language, BookFile, Annotation

#from forms.views_forms import available_languages
from django import forms
from django.forms.widgets import RadioInput

from django.db.models.fields.related import ManyToManyRel

from book.widgets import AuthorWidget, LanguageWidget, AnnotationWidget


CREDIT_CHOICES = (
    ('0', 'DOUBTFUL'),
    ('1', 'CREDIBLE'),
    ('2', 'VERIFIED'),
)


class BookForm(forms.ModelForm):
    '''form for represent model.Book in admin change veiw'''
    class Meta:
        '''defines model for this form '''
        model = Book

    author = forms.CharField(widget=AuthorWidget(rel=ManyToManyRel(to=Author)), 
                                            label='Authors') #TODO help_text
    language = forms.ModelChoiceField(queryset=Language.objects.all(), 
                        widget=LanguageWidget(choices=Language.objects.exclude(book__isnull=True)[1:]))
    credit = forms.IntegerField(widget=forms.RadioSelect(choices=CREDIT_CHOICES))

    annotation = forms.CharField(widget=AnnotationWidget
                                (rel=ManyToManyRel(to=Annotation)))

    def save(self, commit=True):
        """
        Saves this form's data into model using save_book function
        Returns ''instance''.
        """
        if self.instance.pk is None:
            fail_message = 'created'
        else:
            fail_message = 'changed'
        return save_book(self, self.instance, self._meta.fields,
                             fail_message, commit, exclude=self._meta.exclude)


class AuthorForm(forms.ModelForm):
    '''form for represent model.Author in admin change veiw'''
    class Meta:
        '''defines model for this form '''
        model = Author

    credit = forms.IntegerField(widget=forms.Select(choices=CREDIT_CHOICES))

class BookFileForm(forms.ModelForm):
    '''form for represent model.Author in admin change veiw'''
    class Meta:
        '''defines model for this form '''
        model = BookFile

    credit = forms.IntegerField(widget=forms.Select(choices=CREDIT_CHOICES))
    link = forms.CharField(widget=forms.TextInput(attrs={'size':'50'}))
    type = forms.CharField(widget=forms.TextInput(attrs={'size':'50'}))
    img_link = forms.CharField(widget=forms.TextInput(attrs={'size':'50'}), 
                                                                required=False)



def save_book(form, instance, fields=None, fail_message='saved',
                  commit=True, exclude=None):
    """
    Saves book, exracts authors id for saving
    """
    from django.db import models
    opts = instance._meta
    if form.errors:
        raise ValueError("The %s could not be %s because the data didn't"
                         " validate." % (opts.object_name, fail_message))
    cleaned_data = form.cleaned_data

    ############### my logic for saving


    authors_list = eval(cleaned_data.pop('author'))
    authors = list()
    for i in authors_list:
        authors.append(int(i))
    cleaned_data['author'] = authors


    annotations_list = eval(cleaned_data.pop('annotation'))
    annotations = list()
    for i in annotations_list:
        annotations.append(int(i))

    cleaned_data['annotation'] = annotations

    ################

    file_field_list = []
    for field in opts.fields:
        if not field.editable or isinstance(field, models.AutoField) \
                or not field.name in cleaned_data:
            continue
        if fields and field.name not in fields:
            continue
        if exclude and field.name in exclude:
            continue
        # OneToOneField doesn't allow assignment of None. Guard against that
        # instead of allowing it and throwing an error.
        if isinstance(field, models.OneToOneField) and cleaned_data[field.name] is None:
            continue
        # Defer saving file-type fields until after the other fields, so a
        # callable upload_to can use the values from other fields.
        if isinstance(field, models.FileField):
            file_field_list.append(field)
        else:
            field.save_form_data(instance, cleaned_data[field.name])

    for field in file_field_list:
        field.save_form_data(instance, cleaned_data[field.name])

    # Wrap up the saving of m2m data as a function.
    def save_m2m():
        ''' defines how to save object's m2m fields'''
        opts = instance._meta
        cleaned_data = form.cleaned_data
        for field in opts.many_to_many:
            if fields and field.name not in fields:
                continue
            if field.name in cleaned_data:
                field.save_form_data(instance, cleaned_data[field.name])
    if commit:
        # If we are committing, save the instance and the m2m data immediately.
        instance.save()
        save_m2m()
    else:
        # We're not committing. Add a method to the form to allow deferred
        # saving of m2m data.
        form.save_m2m = save_m2m
    return instance


