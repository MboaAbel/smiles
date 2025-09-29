from django.contrib import admin
from django.conf.urls.static import static
from django.urls import include, path
from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import reverse


class StaticSitemap(Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return ['hero', 'blog_page',]

    def location(self, item):
        return reverse(item)

sitemaps = {
       'static': StaticSitemap,
}



urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('__reload__/', include("django_browser_reload.urls")),
    path('admin/', admin.site.urls),
    path('account/', include('allauth.urls')),
    path('', include('Clinic.urls')),
    path('saas/', include('saas.urls')),
    path('bills/', include('billings.urls')),
    path('accounts/', include('Accounts.urls')),
    path('dashboard/', include('Dashboard.urls')),
    path('doctors/', include('doctors.urls')),
    path('mpesa/', include('mpesa.urls')),
    path('reception/', include('bookings.urls')),
    path('patients/', include('patients.urls')),
    path('slots/', include('slots.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns = urlpatterns+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

