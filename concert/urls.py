from django.contrib.sitemaps.views import sitemap
from django.urls import path

from concert import views
from concert.sitemaps import sitemaps
from private_api.views import IncomingPaymentView, MailgunWebhookView, SmtpbzWebhookView

urlpatterns = [
    # concerts
    path('', views.ConcertsView.as_view(), name='concerts'),
    path('<int:concert_id>/', views.ConcertPageView.as_view(), name='concert'),
    path('<int:concert_id>/tickets/', views.BuyTicketView.as_view(), name='buy-ticket'),
    path('<int:concert_id>/email/<int:user>/<str:sha_hash>/', views.ConcertPromoEmailView.as_view(),
         name='concert-promo-email'),

    # tickets
    path('tickets/donepayment/', views.DonePaymentView.as_view(), name='done-payment'),
    path('tickets/mailgun/webhook/<str:event>/', MailgunWebhookView.as_view(),
         name='mailgun-webhook'),
    path('tickets/smtpbz/webhook/<str:event>/', SmtpbzWebhookView.as_view(), name='smtpbz-webhook'),
    path('ticket/<int:ticket>/', views.QRCodeImageView.as_view(), name='qr-code'),

    # emails
    path('email/<int:transaction>/<str:sha_hash>/', views.EmailPageView.as_view(),
         name='email-page'),
    path('email/unsubscribe/<int:user>/<str:sha_hash>/', views.EmailUnsubscribeView.as_view(),
         name='email-unsubscribe'),

    # staff
    path('incomingpayment/', IncomingPaymentView.as_view(), name='incoming-payment'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
]
