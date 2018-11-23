from datetime import datetime
import os

from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse  # from django.core.urlresolvers import reverse in 1.8
import markdown2
from taggit.managers import TaggableManager
from unidecode import unidecode
upload_dir = 'content/BlogPost/%s/%s'
# Create your models here.


class BlogPost(models.Model):

    class Meta:
        ordering = ['-pub_date']    # ordered by pub_date descending when retriving

    def get_upload_md_name(self, filename):
        if self.pub_date:
            year = self.pub_date.year   # always store in pub_year folder
        else:
            year = datetime.now().year
        upload_to = upload_dir % (year, self.title + '.md')
        return upload_to

    def get_html_name(self, filename):
        if self.pub_date:
            year = self.pub_date.year
        else:
            year = datetime.now().year
        upload_to = upload_dir % (year, filename)
        return upload_to

    CATEGORY_CHOICES = (
        ('programming', 'Programming'),
        ('acg', 'animation & summary & machine learning'),
        ('ani', 'Animation'),
        ('ml', 'Machine Learning'),
        ('su', 'Summary'),
        ('nc', 'No Category'),
        ('oth', 'Others'),
    )

    title = models.CharField(max_length=150)
    body = models.TextField(blank=True)
    md_file = models.FileField(upload_to=get_upload_md_name, blank=True)  # uploaded md file
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    last_edit_date = models.DateTimeField('last edited', auto_now=True)
    # The post slug is the user friendly and URL valid name of a post.
    slug = models.SlugField(max_length=200, blank=True)
    html_file = models.FileField(upload_to=get_html_name, blank=True)    # generated html file
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    tags = TaggableManager()

    def __str__(self):
        return self.title   # 根据继承搜索流程,先是实例属性,然后就是类属性,所以这样用没问题

    @property
    def filename(self):
        if self.md_file:
            return os.path.basename(self.title)
        else:
            return 'no md_file'

    def save(self, *args, **kwargs):
        self.slug = slugify(unidecode(self.title))
        if not self.body and self.md_file:
            self.body = self.md_file.read()

        html = markdown2.markdown(self.body,
                                  extras=["fenced-code-blocks", "tables", 'toc','code-friendly'])
        try:
            toc = html.toc_html
            html = toc + html
        except Exception as e:
            pass
        self.html_file.save(self.title + '.html',
                            ContentFile(html.encode('utf-8')), save=False)
        self.html_file.close()

        super().save(*args, **kwargs)

    def display_html(self):
        with open(self.html_file.path, encoding='utf-8') as f:
            return f.read()

    def get_absolute_url(self):
        return reverse('blogpost_slug_id',
                       kwargs={'slug': self.slug, 'post_id': self.id})

    def get_api_absolute_url(self):
        return reverse('api_blogpost_slug_id',
                       kwargs={'slug': self.slug, 'post_id': self.id})


@receiver(pre_delete, sender=BlogPost)
def blogpost_delete(instance, **kwargs):
    if instance.md_file:
        instance.md_file.delete(save=False)
    if instance.html_file:
        instance.html_file.delete(save=False)


class BlogPostImage(models.Model):
    def get_upload_img_name(self, filename):
        upload_to = upload_dir % ('images', filename)  # filename involves extension
        return upload_to

    blogpost = models.ForeignKey(BlogPost, False, related_name='images')
    image = models.ImageField(upload_to=get_upload_img_name)
