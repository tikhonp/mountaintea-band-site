from django.urls import path

from concertstaff import views

urlpatterns = [
    path('', views.MainView.as_view(), name='staff'),
    path('statistic/<int:concert>/', views.StatView.as_view(), name='staff-concert-statistic'),
    path('submit/<int:ticket>/<str:sha>/', views.ticket_check, name='staff-ticket-check'),
    path('submit/<int:ticket>/<str:sha>/data/', views.ticket_check_data, name='staff-ticket-check-data'),
    path('newfreeticket/', views.add_ticket, name='staff-free-ticket'),
    path('submitnumber/', views.submit_number, name='submit-number'),
    path('issue/<int:issue>/', views.issue_page, name='issue'),
    path('qrcode/', views.qrcode, name='qrcode'),
    path('concerts/data/', views.concerts_data, name='concerts-data'),
]
