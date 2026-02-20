from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    barcode = models.CharField(max_length=100, unique=True, help_text="Scan barcode here")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    image = models.FileField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.barcode})"
