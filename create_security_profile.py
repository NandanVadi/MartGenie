import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'martgenie.settings')
django.setup()

from accounts.models import CustomUser, SecurityProfile
from core.models import Store

def create_profile():
    try:
        user = CustomUser.objects.get(username='GUARD001')
        store = Store.objects.first() # Assign to the first store
        
        if not store:
            print("No store found! Creating one...")
            store = Store.objects.create(name="MartGenie HQ", store_code="HQ001", address="123 Tech Park")

        profile, created = SecurityProfile.objects.get_or_create(
            user=user,
            defaults={
                'store': store,
                'employee_id': 'EMP-001',
                'shift_start': datetime.time(9, 0),
                'shift_end': datetime.time(18, 0),
            }
        )
        
        if created:
            print(f"Created Security Profile for {user.username} at {store.name}")
        else:
            print(f"Security Profile already exists for {user.username}")
            
    except CustomUser.DoesNotExist:
        print("GUARD001 user not found. Please run fix_users_and_roles.py first.")

if __name__ == '__main__':
    create_profile()
