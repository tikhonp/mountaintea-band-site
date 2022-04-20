from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib import sitemaps
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.urls import reverse

from concert import views
from concert.sitemaps import concert_sitemaps


admin.site.site_header = 'MountainTea administration'
admin.site.site_title = 'MountainTea site admin'


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        return ['main']

    def location(self, item):
        return reverse(item)


sitemaps = {
    'static': StaticViewSitemap,
}
sitemaps.update(concert_sitemaps)

urlpatterns = [
    path('', views.main, name='main'),
    path('admin/', admin.site.urls, name='admin'),
    path('concerts/', include('concert.urls')),
    path('staff/', include('concertstaff.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
