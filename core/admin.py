from django.contrib import admin
from .models import Store

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'store_code', 'address', 'is_active')
    search_fields = ('name', 'store_code')
