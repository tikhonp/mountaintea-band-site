from django.urls import path

from concertstaff import views

urlpatterns = [
    path('', views.MainView.as_view(), name='staff'),
    path('statistic/<int:concert>/', views.StatView.as_view(), name='staff-concert-statistic'),
    path('submit/<int:ticket>/<str:sha>/', views.TicketCheckView.as_view(), name='staff-ticket-check'),
    path('newfreeticket/', views.AddTicketFormView.as_view(), name='staff-free-ticket'),
    path('submitnumber/', views.SubmitNumberView.as_view(), name='submit-number'),
    path('issue/<int:issue>/', views.IssuePageView.as_view(), name='issue'),
    path('qrcode/', views.QRCodeView.as_view(), name='qrcode'),
]
