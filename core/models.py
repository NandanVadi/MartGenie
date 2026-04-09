from django.db import models
from django.conf import settings

class Store(models.Model):
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='managed_stores', null=True, blank=True)
    name = models.CharField(max_length=100)
    store_code = models.CharField(max_length=20, unique=True, help_text='Unique code for the store (e.g., 1001, MG01)')
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.store_code})"

class Promotion(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=200)
    icon = models.CharField(max_length=50, default='percent', help_text='Lucide icon name (e.g., percent, award, shopping-bag)')
    color_hex = models.CharField(max_length=7, default='#3b82f6', help_text='Hex color for the brand (e.g., #3b82f6 for blue)')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

