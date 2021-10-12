"""gornijchaij URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib import sitemaps
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.urls import reverse

from concert import views
from concert.sitemaps import concert_sitemaps


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
