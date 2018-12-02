import platform
import os

from django import forms
from django.conf import settings
from django.contrib import admin
from django.core.files.base import ContentFile
from django.forms import TextInput, Textarea

from .models import BlogPost, BlogPostImage







class BlogPostImageInline(admin.TabularInline):
    model = BlogPostImage
    extra = 3


class BlogPostAdminForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        widgets = {
            'body': Textarea(attrs={'rows': 100, 'cols': 100}),
            'title': TextInput(attrs={'size': 40}),
        }
        exclude = ()


class BlogPostAdmin(admin.ModelAdmin):

    form = BlogPostAdminForm
    inlines = [BlogPostImageInline]

    @staticmethod
    def delete_old_md_file():
        # delete old md files, this method is unused now
        md_file_list = []
        for blogpost in BlogPost.objects.all():
            if blogpost.md_file:
                md_file_list.append(blogpost.filename)

        with open('md_file_list.txt', 'wt') as f:
            f.write(str(md_file_list))

        for root, subdirs, files in os.walk(os.path.join(settings.MEDIA_ROOT, 'content/BlogPost')):
            for file in files:
                if file not in md_file_list:
                    os.remove(os.path.join(root, file))

    def save_model(self, request, obj, form, change):
        if obj:
            if obj.body:   # body有内容的时候才会更新md_file
                filename = obj.filename
                if filename != 'no md_file':
                    # On Windows file can't be removed so leave it
                    if platform.system() == "Windows":
                        pass
                    else:
                        obj.md_file.delete(save=False)   # 部署的时候存在,可以正常删除文件
                        obj.html_file.delete(save=False)
                # 没有md_file就根据title创建一个, 但不能创建html因为obj.save()的时候会创建
                obj.md_file.save(filename+'.md', ContentFile(obj.body), save=False)
                obj.md_file.close()
        obj.save()

# Register your models here.
admin.site.register(BlogPost, BlogPostAdmin)