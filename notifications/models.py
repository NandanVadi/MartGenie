from django.db import models

class Notification(models.Model):
    TYPE_CHOICES = (
        ('LOW_STOCK', 'Low Stock'),
        ('SYSTEM', 'System'),
    )

    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='SYSTEM')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.message[:50]}"
        
    @property
    def type_display(self):
        return self.get_notification_type_display()
