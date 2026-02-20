from django.contrib import admin
from .models import Order, OrderItem, GatePassLog

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class GatePassLogInline(admin.TabularInline):
    model = GatePassLog
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'store', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'store')
    search_fields = ('order_id', 'user__username', 'user__phone_number')
    inlines = [OrderItemInline, GatePassLogInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'order', 'quantity', 'price')

@admin.register(GatePassLog)
class GatePassLogAdmin(admin.ModelAdmin):
    list_display = ('order', 'guard', 'status', 'verified_at')
    list_filter = ('status', 'verified_at', 'guard')
    search_fields = ('order__order_id', 'guard__username')
