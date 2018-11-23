from collections import defaultdict
import json
from math import ceil

from django.core import serializers
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.urls import reverse

from .models import BlogPost
# Create your views here.
# api version
exclude_posts = ("shares","Happy Birthday To My Princess",)


def args_generator(args, blogposts):
    contents = [blogquery.display_html() for blogquery in blogposts]
    urls = [blogquery.get_api_absolute_url() for blogquery in blogposts]
    alltags = [blogquery.tags.all() for blogquery in blogposts]
    bolgList = json.loads(serializers.serialize("json", blogposts))

    for index in range(len(bolgList)):
        bolgList[index]['content'] = contents[index]
        bolgList[index]['tags'] = json.loads(serializers.serialize("json", alltags[index]))
        bolgList[index]['url'] = urls[index]
    args['blogposts'] = bolgList
    args['blogpostsnum'] = len(args['blogposts'])


def entire_blogpost(blogpost):
    content = blogpost.display_html()
    url = blogpost.get_api_absolute_url()
    alltags = blogpost.tags.all()
    blogpost_json = json.loads(serializers.serialize("json", [blogpost]))
    blogpost_json = blogpost_json[0]
    blogpost_json['content'] = content
    blogpost_json['url'] = url
    blogpost_json['tags'] = json.loads(serializers.serialize("json", alltags))
    return blogpost_json


def split_page(args, blogposts, page):
    max_page = ceil(len(args['blogposts']) / 3)
    page = int(page) if (page and int(page) > 0) else 1
    args['page'] = page
    args['prev_page'] = page + 1 if page < max_page else None
    args['newer_page'] = page - 1 if page > 1 else None  # if page rows then the new_page is not none
    # as template slice filter, syntax: list|slice:"start:end"
    args['sl'] = str(3 * (page - 1)) + ':' + str(3 * (page - 1) + 3)
    args['max_page'] = max_page


def api_allblogs(request, page=''):
    args = dict()

    blogposts = BlogPost.objects.exclude(title__in=exclude_posts)
    args_generator(args, blogposts)

    if page and int(page) < 2:  # /0, /1 -> /
        return redirect("/blog/api/allblogs/")
    else:
        split_page(args, blogposts, page)
        # return render(request, 'css3template_blog/' + page_html, args)
        return JsonResponse(args)


def api_tagblog(request, tag, page=''):
    args = dict()
    print(tag)
    args['tag'] = tag
    blogposts= BlogPost.objects.filter(tags__name__in=[tag, ])
    args_generator(args, blogposts)

    if page and int(page) < 2:  # /0, /1 -> /
        return redirect(reverse('api_tag', kwargs={'tag': tag}))
    else:
        split_page(args, blogposts, page)
        # return render(request, 'css3template_blog/' + page_html, args)
        return JsonResponse(args)


def api_blogpost(request, slug, post_id):
    blogpost = get_object_or_404(BlogPost, pk=post_id)
    blogpost_json = entire_blogpost(blogpost)
    args = {'blogpost': blogpost_json}
    return JsonResponse(args)


def api_archive(request):
    args = dict()
    blogposts = BlogPost.objects.exclude(title__in=exclude_posts)

    def get_sorted_posts(category):
        posts_by_year = defaultdict(list)
        posts_of_a_category = blogposts.filter(category=category)  # already sorted by pub_date
        for post in posts_of_a_category:
            year = post.pub_date.year
            blogpost_json = entire_blogpost(post)
            posts_by_year[year].append(blogpost_json)  # {'2013':post_list, '2014':post_list}
        posts_by_year = sorted(posts_by_year.items(), reverse=True)  # [('2014',post_list), ('2013',post_list)]
        return posts_by_year

    args['data'] = [
        ('programming', get_sorted_posts(category="programming")),
        ('ani', get_sorted_posts(category="ani")),
        ('ml', get_sorted_posts(category="ml")),
        ('su', get_sorted_posts(category="su")),
        ('oth', get_sorted_posts(category="oth")),
    ]
    return JsonResponse(args)

def api_shares(request):
    the_talks_post = get_object_or_404(BlogPost, title="shares")
    blogpost_json = entire_blogpost(the_talks_post)
    args = {"shares": blogpost_json}
    return JsonResponse(args)