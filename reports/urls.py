from django.urls import path
from . import views

urlpatterns = [
    path("revenue/", views.revenue_report, name="revenue_report"),
    path("room/", views.room_report, name="room_report"),
    path("order/", views.order_report, name="order_report"),
]
