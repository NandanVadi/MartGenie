import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'martgenie.settings')
django.setup()

from accounts.models import CustomUser

def fix_users():
    # Fix Admin User
    admin_user, created = CustomUser.objects.get_or_create(username='ADMIN001')
    admin_user.set_password('ADMIN123')
    admin_user.role = 'ADMIN'
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.is_active = True
    admin_user.save()
    print(f"ADMIN001 updated: Role={admin_user.role}, Staff={admin_user.is_staff}, Superuser={admin_user.is_superuser}")

    # Fix Security User
    security_user, created = CustomUser.objects.get_or_create(username='GUARD001')
    security_user.set_password('GUARD123')
    security_user.role = 'SECURITY'
    security_user.is_staff = True  # Optional: allow them to log into admin to view orders if needed
    security_user.is_superuser = False
    security_user.is_active = True
    security_user.save()
    print(f"GUARD001 updated: Role={security_user.role}, Staff={security_user.is_staff}")

if __name__ == '__main__':
    fix_users()
