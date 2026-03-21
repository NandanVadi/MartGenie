from django.contrib import admin
from .models import Store

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'store_code', 'admin', 'address', 'is_active')
    search_fields = ('name', 'store_code', 'admin__username')
