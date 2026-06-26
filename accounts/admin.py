from django.contrib import admin
from .models import User, Customer, OperationLog, PointsRecord

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'real_name', 'role', 'phone', 'is_active', 'created_at']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'real_name', 'phone']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['phone', 'real_name', 'member_level', 'points', 'total_spent', 'created_at']
    search_fields = ['phone', 'real_name']

@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ['operator', 'action_type', 'content', 'ip_address', 'created_at']
    list_filter = ['action_type']
    search_fields = ['operator__username']

@admin.register(PointsRecord)
class PointsRecordAdmin(admin.ModelAdmin):
    list_display = ['customer', 'change_amount', 'change_type', 'remaining', 'created_at']
