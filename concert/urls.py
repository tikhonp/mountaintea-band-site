from django.contrib.sitemaps.views import sitemap
from django.urls import path

from concert import views
from concert.sitemaps import sitemaps

urlpatterns = [
    path('', views.ConcertsView.as_view(), name='concerts'),
    path('<int:concert_id>/', views.ConcertPageView.as_view(), name='concert'),
    path('<int:concert_id>/tickets/', views.BuyTicketView.as_view(), name='buy-ticket'),
    path('<int:concert_id>/email/<int:user>/<str:sha_hash>/', views.ConcertPromoEmailView.as_view(),
         name='concert-promo-email'),
    path('incomingpayment/', views.IncomingPaymentView.as_view(), name='incoming-payment'),
    path('tickets/donepayment/', views.DonePaymentView.as_view(), name='done-payment'),
    path('tickets/mailgun/webhook/<str:event>/', views.MailgunWebhookView.as_view(), name='mailgun-webhook'),
    path('ticket/<int:ticket>/', views.QRCodeImageView.as_view(), name='qr-code'),
    path('email/<int:transaction>/<str:sha_hash>/', views.EmailPageView.as_view(), name='email-page'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('email/unsubscribe/<int:user>/<str:sha_hash>/', views.EmailUnsubscribeView.as_view(), name='email-unsubscribe'),
]
