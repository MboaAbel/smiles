from django.db import models
from ckeditor.fields import RichTextField
import random
import uuid


class Page(models.Model):
    pagetitle = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    aboutus = models.TextField()
    email = models.EmailField(max_length=200)
    mobilenumber = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.pagetitle

class Blog(models.Model):
    soshi_user = models.CharField(max_length=100)
    blog_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    blog_title = models.CharField(max_length=250)
    blog_subtitle = models.CharField(max_length=250)
    caption = RichTextField(blank=True)
    blog_image = models.ImageField(upload_to='blog_photos/', null=False, default='icon/bondijunction_dentalclinic_logo-300x258.jpg', blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.blog_id}'
