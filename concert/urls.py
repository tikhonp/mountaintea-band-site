from django.urls import path
from concert import views


urlpatterns = [
    path('', views.concerts, name='Список концертов'),
    path('<int:concert_id>/', views.concert_page, name='Лендинг концерта'),
    path(
        '<int:concert_id>/tickets/', views.buy_ticket, name='Покупка билета'),
    path('incomingpayment/', views.incoming_payment, name='Входящий платеж'),
    path('tickets/donepayment/', views.done_payment, name='Платеж совершен'),
    path('ticket/<int:ticket>/', views.qr_codeimage, name='qr код'),
]
