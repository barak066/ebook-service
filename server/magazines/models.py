# -*- coding: utf-8 -*-
from django.db import models


NAME_LENGTH = 255
LINK_LENGTH = 4000
TEXT_LENGTH = 10000


class Magazine(models.Model):
    name = models.CharField(unique=True, max_length=NAME_LENGTH)
    link = models.CharField(max_length=LINK_LENGTH, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    cover = models.ImageField(upload_to="covers", null=True, blank=True)

    def __unicode__(self):
        return '%s' % self.name


class Category(models.Model):
    name = models.CharField(unique=True, max_length=NAME_LENGTH)
    def __unicode__(self):
       return u'%s' % self.name

    class Meta:
        verbose_name_plural = "categories"

class Issue(models.Model):
    magazine = models.ForeignKey(Magazine)
    year = models.IntegerField()
    number = models.IntegerField()
    def __unicode__(self):
       return u'%d/%d (%s)' % (self.year, self.number, self.magazine.name )
    def get_link(self):
        return '%s%d/%d/' % (self.magazine.link, self.year, self.number)


class Article(models.Model):
    link = models.CharField(unique=True, max_length=255) #255 because of django constrains (when unique = True)
    title = models.CharField(max_length=NAME_LENGTH)
    issue = models.ForeignKey(Issue)
    authors = models.CharField(max_length=NAME_LENGTH, null=True, blank=True)
    category = models.ManyToManyField(Category, null=True, blank=True)
    description = models.TextField(max_length=TEXT_LENGTH, null=True,blank=True)
    
    def __unicode__(self):
        return u'(%s) %s' % (self.issue,self.title,)
