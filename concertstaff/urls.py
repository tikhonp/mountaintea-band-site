from django.urls import path
from concertstaff import views

urlpatterns = [
    path('', views.main),
    path('statistic/<int:concert>/', views.stat),
    path('submit/<int:ticket>/<str:sha>/', views.ticket_check),
    path('test/<int:transaction>/', views.test),
    path('newfreeticket/', views.add_ticket),
    path('submitnumber/', views.submit_number),
]
