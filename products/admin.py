from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'barcode', 'price', 'category')
    search_fields = ('name', 'barcode')
    list_filter = ('category',)
