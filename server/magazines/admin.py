# -*- coding: utf-8 -*-

from django.contrib import admin
from models import Magazine, Category, Article, Issue

class MagazineAdmin(admin.ModelAdmin):
    list_display = ('name', 'link', 'about')
    list_per_page = 15
    pass

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_per_page = 30
    pass

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'issue', 'link')
    list_per_page = 30
    pass

class IssueAdmin(admin.ModelAdmin):
    list_display = ('magazine', 'year', 'number')
    list_per_page = 30
    list_filter = ('year','magazine')
    pass

admin.site.register(Magazine, MagazineAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Issue, IssueAdmin)

