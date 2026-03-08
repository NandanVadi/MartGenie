from django.db import models
from core.models import Store
from products.models import Product

class InventoryItem(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='inventory')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_items')
    quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5, help_text="Notify when stock falls below this level")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('store', 'product')
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"

    def is_low_stock(self):
        """
        Returns True if the current quantity is below the configured threshold.
        Useful for dashboard alerts and monitoring.
        """
        return self.quantity < self.low_stock_threshold

    def __str__(self):
        return f"{self.product.name} - {self.quantity} left in {self.store.name}"
