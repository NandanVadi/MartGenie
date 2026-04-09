from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import InventoryItem
from notifications.models import Notification

@receiver(post_save, sender=InventoryItem)
def check_low_stock(sender, instance, **kwargs):
    """
    Signal to check if an inventory item falls below its low stock threshold.
    Creates a notification if it does.
    """
    if instance.is_low_stock():
        # Check if an unread low stock notification already exists for this product in this store
        existing_notif = Notification.objects.filter(
            store=instance.store,
            notification_type='LOW_STOCK',
            message__contains=instance.product.name,
            is_read=False
        ).exists()

        if not existing_notif:
            Notification.objects.create(
                store=instance.store,
                message=f"Low Stock Alert: {instance.product.name} (Qty: {instance.quantity}) in {instance.store.name}",
                notification_type='LOW_STOCK'
            )
