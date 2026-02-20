
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'martgenie.settings')
django.setup()

from core.models import Store
from accounts.models import CustomUser

def seed():
    # Create Store
    store, created = Store.objects.get_or_create(
        store_code="MARTGENIE-STORE-001",
        defaults={
            "name": "MartGenie Demo Store",
            "address": "123 Tech Park, Bangalore",
            "is_active": True
        }
    )
    if created:
        print(f"Created Store: {store}")
    else:
        print(f"Store already exists: {store}")

    # Create Admin
    admin_id = "ADMIN001"
    admin_pass = "ADMIN123"
    if not CustomUser.objects.filter(username=admin_id).exists():
        CustomUser.objects.create_superuser(
            username=admin_id,
            password=admin_pass,
            role="ADMIN"
        )
        print(f"Created Admin: {admin_id} / {admin_pass}")
    else:
        print(f"Admin already exists: {admin_id}")

    # Create Guard
    guard_id = "GUARD001"
    guard_pass = "GUARD123"
    if not CustomUser.objects.filter(username=guard_id).exists():
        user = CustomUser.objects.create_user(
            username=guard_id,
            password=guard_pass,
            role="SECURITY"
        )
        print(f"Created Guard: {guard_id} / {guard_pass}")
    else:
        print(f"Guard already exists: {guard_id}")

    # Create Customer for testing
    phone = "9876543210"
    if not CustomUser.objects.filter(username=phone).exists():
        CustomUser.objects.create_user(
            username=phone,
            phone_number=phone,
            role="CUSTOMER"
        )
        print(f"Created Demo Customer: {phone}")

if __name__ == "__main__":
    seed()
