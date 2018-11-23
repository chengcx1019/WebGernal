#!/usr/bin/env python
# encoding: utf-8

"""
@author: changxin
@mail: chengcx1019@gmail.com
@file: urls.py
@time: 2018/7/5 19:46
"""
from django.urls import path,re_path
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
    # path(r'', TemplateView.as_view(template_name='index.html')),
    re_path(r'^api/allblogs/(?P<page>\d*)', views.api_allblogs),
    re_path(r'^api/tag/(?P<tag>[-\w\d]+),(?P<page>\d+)?/$', views.api_tagblog, name='api_tag'),
    re_path(r'^api/(?P<slug>[-\w\d]+),(?P<post_id>\d+)/$', views.api_blogpost, name='api_blogpost_slug_id'),
    re_path('^api/archive', views.api_archive, name='api_archive'),
    re_path('^api/shares', views.api_shares, name='api_shares'),
]


if __name__ == '__main__':
    pass
