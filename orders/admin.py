from django.contrib import admin
from .models import Order, ConsumptionBill, CleaningTask

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "room", "check_in", "check_out", "status", "final_amount"]
    list_filter = ["status"]
    search_fields = ["id", "customer__phone"]

@admin.register(ConsumptionBill)
class ConsumptionBillAdmin(admin.ModelAdmin):
    list_display = ["order", "bill_type", "amount", "created_at"]

@admin.register(CleaningTask)
class CleaningTaskAdmin(admin.ModelAdmin):
    list_display = ["room", "cleaner", "status", "created_at"]
    list_filter = ["status"]
