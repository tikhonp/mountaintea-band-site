from django.urls import path

from concertstaff import views

urlpatterns = [
    path('', views.main, name='staff'),
    path('statistic/<int:concert>/', views.stat, name='staff-concert-statistic'),
    path('statistic/<int:concert>/data/', views.stat_data, name='staff-concert-statistic-data'),
    path('submit/<int:ticket>/<str:sha>/', views.ticket_check, name='staff-ticket-check'),
    path('submit/<int:ticket>/<str:sha>/data/', views.ticket_check_data, name='staff-ticket-check-data'),
    path('newfreeticket/', views.add_ticket, name='staff-free-ticket'),
    path('submitnumber/', views.submit_number, name='submit-number'),
    path('issue/<int:issue>/', views.issue_page, name='issue'),
    path('qrcode/', views.qrcode, name='qrcode'),
    path('concerts/data/', views.concerts_data, name='concerts-data'),
]
