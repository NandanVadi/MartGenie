import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'martgenie.settings')
django.setup()

from billing.models import Order

print(f"Total Orders: {Order.objects.count()}")
for order in Order.objects.all():
    print(f"ID: {order.id} | OrderID: '{order.order_id}' | Amount: {order.total_amount}")
    for item in order.items.all():
        print(f"  - Item: {item.product_name} | Qty: {item.quantity} (Type: {type(item.quantity)}) | Price: {item.price}")
