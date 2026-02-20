import os
import django
import sys
import pytz
from django.utils import timezone

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "martgenie.settings")
django.setup()

from billing.models import Order

print(f"Server Time (UTC): {timezone.now()}")
ist = pytz.timezone('Asia/Kolkata')

orders = Order.objects.order_by('-created_at')[:10]
for o in orders:
    local_time = o.created_at.astimezone(ist)
    print(f"ID: {o.order_id} | UTC: {o.created_at} | IST: {local_time}")
