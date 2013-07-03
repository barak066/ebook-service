# -*- coding: utf-8 -*-


from django.contrib import admin

from models import Task, Refresh






class TaskAdmin(admin.ModelAdmin):
    search_fields = ('link', )
    list_display = ('name', 'parser_name', 'weight', 'link','good', 'when')
    list_filter = ('parser_name','good','weight', 'name')

    fields = ('name', 'parser_name', 'weight', 'link', 'good','reason')
    list_per_page = 30
    actions = ['make_good']

    def make_good(self,request, queryset):
        """ Make all task  published. """
        queryset.update(good=True)
        count = queryset.filter(good=False).update(good=True)
        self.message_user(request, '%s posts mark as good.' % count)
    make_good.short_description = "Mark selected tasks as good"

class RefreshAdmin(admin.ModelAdmin):
    search_fields = ('link', )
    list_display = ('link', 'last_modified')

    fields = ('link', 'last_modified')
    list_per_page = 30
    


admin.site.register(Task, TaskAdmin)
admin.site.register(Refresh, RefreshAdmin)
