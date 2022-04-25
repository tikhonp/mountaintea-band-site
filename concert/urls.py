from django.contrib.sitemaps.views import sitemap
from django.urls import path

from concert import views
from concert.sitemaps import sitemaps

urlpatterns = [
    path('', views.concerts, name='concerts'),
    path('<int:concert_id>/', views.concert_page, name='concert'),
    path('<int:concert_id>/tickets/', views.buy_ticket, name='buy-ticket'),
    path('<int:concert_id>/tickets/data/', views.buy_ticket_data, name='buy-ticket-data'),
    path('<int:concert_id>/email/<int:user>/<str:sha_hash>/', views.concert_promo_email, name='concert-promo-email'),
    path('incomingpayment/', views.incoming_payment, name='incoming-payment'),
    path('tickets/donepayment/', views.done_payment, name='done-payment'),
    path('tickets/mailgun/webhook/<str:event>/', views.mailgun_webhook, name='mailgun-webhook'),
    path('ticket/<int:ticket>/', views.qr_code_image, name='qr-code'),
    path('email/<int:transaction>/<str:sha_hash>/', views.email_page, name='email-page'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('email/unsubscribe/<int:user>/<str:sha_hash>/', views.email_unsubscribe, name='email-unsubscribe'),
    path('issue/', views.add_issue, name='add-issue'),
]
