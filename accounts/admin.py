from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, SecurityProfile

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'phone_number', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone_number', 'role')}),
    )

class SecurityProfileInline(admin.StackedInline):
    model = SecurityProfile
    can_delete = False
    verbose_name_plural = 'Security Profile'

class CustomUserAdminWithProfile(CustomUserAdmin):
    inlines = (SecurityProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdminWithProfile, self).get_inline_instances(request, obj)

# Unregister original CustomUserAdmin if needed, or just register our new one
# Since we are redefining how CustomUser is registered
try:
    admin.site.unregister(CustomUser)
except admin.sites.NotRegistered:
    pass

admin.site.register(CustomUser, CustomUserAdminWithProfile)

@admin.register(SecurityProfile)
class SecurityProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'store', 'is_active')
    search_fields = ('user__username', 'employee_id', 'store__name')
