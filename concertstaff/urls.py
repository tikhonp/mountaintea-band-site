from django.urls import path

from concertstaff import views

urlpatterns = [
    path('', views.main, name='staff'),
    path('statistic/<int:concert>/', views.stat, name='staff-concert-statistic'),
    path('submit/<int:ticket>/<str:sha>/', views.ticket_check, name='staff-ticket-check'),
    path('test/<int:transaction>/', views.test, name='staff-test-transaction'),
    path('newfreeticket/', views.add_ticket, name='staff-free-ticket'),
    path('submitnumber/', views.submit_number, name='submit-number'),
]
