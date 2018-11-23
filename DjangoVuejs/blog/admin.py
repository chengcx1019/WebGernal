from django.contrib import admin
from .models import BlogPost, BlogPostImage
# Register your models here.
admin.site.register(BlogPost)
admin.site.register(BlogPostImage)