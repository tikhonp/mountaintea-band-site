from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from private_api import views
from django.conf import settings

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()
router.register(r'concerts', views.ConcertViewSet, basename="concerts")
router.register(r'prices', views.PriceViewSet, basename="prices")
router.register(r'user', views.CurrentUserViewSet, basename="currant user vs")
router.register(r'issues', views.IssueViewSet, basename="issues")
router.register(r'tickets', views.TicketViewSet, basename="tickets")

urlpatterns = [
    path('', include(router.urls)),
    path('buy/ticket/', views.BuyTicketApiView.as_view(), name="buy-ticket-endpoint")
]
