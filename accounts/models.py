from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import Store

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('CUSTOMER', 'Customer'),
        ('ADMIN', 'Admin'),
        ('SECURITY', 'Security'),
    )

    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CUSTOMER')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class SecurityProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='security_profile')
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, related_name='security_guards')
    employee_id = models.CharField(max_length=20, unique=True)
    shift_start = models.TimeField(null=True, blank=True)
    shift_end = models.TimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.employee_id}
