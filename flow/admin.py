from django.contrib import admin
from .models import SKU, Order, OrderLine

class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "customer_name", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("order_number", "customer_name")
    inlines = [OrderLineInline]

admin.site.register(SKU)