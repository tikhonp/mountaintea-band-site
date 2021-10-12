from django.contrib.sitemaps.views import sitemap
from django.urls import path

from concert import views
from concert.sitemaps import sitemaps

urlpatterns = [
    path('', views.concerts, name='concerts'),
    path('<int:concert_id>/', views.concert_page, name='concert'),
    path('<int:concert_id>/tickets/', views.buy_ticket, name='buy-ticket'),
    path('incomingpayment/', views.incoming_payment, name='incoming-payment'),
    path('tickets/donepayment/', views.done_payment, name='done-payment'),
    path('ticket/<int:ticket>/', views.qr_code_image, name='qr-code'),
    path('email/<int:transaction>/<str:sha_hash>/', views.email_page, name='email-page'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
