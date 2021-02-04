from django.urls import path
from concert import views


urlpatterns = [
    path('', views.main_page, name='Лендинг концерта'),
    path(
        'tickets/<int:concert_id>/', views.buy_ticket, name='Покупка билета'),
    path('incomingpayment/', views.incoming_payment, name='Входящий платеж'),
]
