from django.contrib import admin

# Register your models here.
from .models import Page, Blog

# Register your models here.

admin.site.register(Page)
admin.site.register(Blog)
