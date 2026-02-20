from django.db import models
from django.conf import settings
from core.models import Store

class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True)
    order_id = models.CharField(max_length=20, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    qr_data = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.order_id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    product_id = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

class GatePassLog(models.Model):
    guard = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='verified_gate_passes')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='gate_pass_logs')
    verified_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=(('APPROVED', 'Approved'), ('REJECTED', 'Rejected')), default='APPROVED')
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Pass {self.order.order_id} - {self.status}"
