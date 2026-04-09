from django.urls import path
from . import views, admin_views

urlpatterns = [
    path('', views.home, name='home'),
    path('cart/', views.cart_view, name='cart'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
    
    # Admin Management Routes
    path('dashboard/management/', admin_views.admin_management, name='admin_management'),
    path('dashboard/management/add-store/', admin_views.add_store_api, name='add_store_api'),
    path('dashboard/management/add-security/', admin_views.create_security_api, name='create_security_api'),
    path('dashboard/sales/', views.sales_ledger, name='sales_ledger'),
    path('dashboard/customers/', views.customers_crm, name='customers_crm'),
]
