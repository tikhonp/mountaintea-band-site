from django.contrib.sitemaps import GenericSitemap, Sitemap
from django.urls import reverse

from concert.models import Concert


class ConcertStaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['concerts']

    def location(self, item):
        return reverse(item)


concert_sitemaps = {
    'static_concert': ConcertStaticViewSitemap,
    'concerts': GenericSitemap({'queryset': Concert.objects.all()}, priority=0.6),
}
