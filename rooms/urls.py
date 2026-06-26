from django.urls import path
from . import views

urlpatterns = [
    path("hotel/", views.hotel_config, name="hotel_config"),
    path("types/", views.room_type_list, name="room_type_list"),
    path("types/create/", views.room_type_create, name="room_type_create"),
    path("types/edit/<int:pk>/", views.room_type_edit, name="room_type_edit"),
    path("", views.room_list, name="room_list"),
    path("create/", views.room_create, name="room_create"),
    path("edit/<int:pk>/", views.room_edit, name="room_edit"),
    path("status/<int:pk>/", views.room_status_update, name="room_status_update"),
]
