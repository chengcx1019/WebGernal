#!/usr/bin/env python
# encoding: utf-8

"""
@author: changxin
@mail: chengcx1019@gmail.com
@file: feeds.py
@time: 2018/11/24 01:41
"""

from django.contrib.syndication.views import Feed
from django.urls import reverse

from .models import BlogPost

class LatestEntriesFeed(Feed):
    title = "Unity of knowlege and practice"
    link = "/blog/api/allblogs/"
    description = "Updates on changes and additions to police beat central."

    def items(self):
        return BlogPost.objects.order_by('-pub_date')[:5]  # '-pub_date' represent the lastest

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.get_absolute_url()

    # item_link is only needed if NewsItem has no get_absolute_url method.
    # def item_link(self, item):
    #     return reverse('news-item', args=[item.pk])

if __name__ == '__main__':
    import os
