# -*- coding: utf-8 -*-
from server.django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
          (r'^$', views.list),
          #(r'^list/?$', views.list),
          (r'^(\d{1,})/$', views.show_years),
          (r'^(\d{1,})/(\d{4})/$', views.show_issues),
          (r'^(\d{1,})/(\d{4})/(\d{1,})/$', views.show_articles),
          (r'^generate/(\d{1,})', views.generate_epub),
        )
