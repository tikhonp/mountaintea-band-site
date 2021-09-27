from django.urls import path

from concert import views

urlpatterns = [
    path('', views.concerts, name='concerts'),
    path('<int:concert_id>/', views.concert_page, name='concert'),
    path('<int:concert_id>/tickets/', views.buy_ticket, name='buy-ticket'),
    path('incomingpayment/', views.incoming_payment, name='incoming-payment'),
    path('tickets/donepayment/', views.done_payment, name='done-payment'),
    path('ticket/<int:ticket>/', views.qr_codeimage, name='qr-code'),
    path('email/<int:transaction>/<str:sha_hash>/', views.email_page, name='email-page'),
]
