from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Service  # Assuming you have a Service model

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['home', 'about', 'contact']  # List of view names

    def location(self, item):
        return reverse(item)

class ServiceSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Service.objects.all()

    def lastmod(self, obj):
        return obj.updated_at
