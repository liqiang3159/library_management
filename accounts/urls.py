from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/edit/<int:pk>/', views.employee_edit, name='employee_edit'),
    path('customers/', views.customer_list, name='customer_list'),
    path('logs/', views.operation_log_list, name='log_list'),
]
