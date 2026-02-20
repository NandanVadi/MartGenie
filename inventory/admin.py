from django.contrib import admin
from .models import InventoryItem

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'store', 'quantity', 'low_stock_threshold')
    search_fields = ('product__name', 'store__name')
    list_filter = ('store',)
    autocomplete_fields = ['product', 'store']
