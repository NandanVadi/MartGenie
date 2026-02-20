from django.db import models

class Store(models.Model):
    name = models.CharField(max_length=100)
    store_code = models.CharField(max_length=20, unique=True, help_text='Unique code for the store (e.g., 1001, MG01)')
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.store_code})"

