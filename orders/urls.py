from django.urls import path
from . import views

urlpatterns = [
    path("", views.order_list, name="order_list"),
    path("create/", views.order_create, name="order_create"),
    path("<int:pk>/", views.order_detail, name="order_detail"),
    path("<int:pk>/checkin/", views.order_check_in, name="order_check_in"),
    path("<int:pk>/checkout/", views.order_check_out, name="order_check_out"),
    path("<int:pk>/settle/", views.order_settle, name="order_settle"),
    path("<int:pk>/cancel/", views.order_cancel, name="order_cancel"),
    path("<int:pk>/consumption/", views.add_consumption, name="add_consumption"),
    path("cleaning/", views.cleaning_list, name="cleaning_list"),
    path("cleaning/<int:pk>/", views.cleaning_update, name="cleaning_update"),
]
