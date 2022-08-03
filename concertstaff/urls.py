from django.urls import path

from concertstaff import views

urlpatterns = [
    # Main staff page with issues list
    path('', views.MainView.as_view(), name='staff'),

    # Concert ticket statistic
    path('statistic/<int:concert>/', views.StatView.as_view(), name='staff-concert-statistic'),

    # Check ticket pages
    path('submitnumber/', views.SubmitNumberView.as_view(), name='submit-number'),
    path('submit/<int:ticket>/<str:sha>/', views.TicketCheckView.as_view(), name='staff-ticket-check'),
    path('qrcode/', views.QRCodeView.as_view(), name='qrcode'),

    # Add new ticket
    path('newfreeticket/', views.AddTicketFormView.as_view(), name='staff-free-ticket'),

    # Issue page
    path('issue/<int:issue>/', views.IssuePageView.as_view(), name='issue'),
]
