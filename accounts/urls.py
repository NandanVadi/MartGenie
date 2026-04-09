from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_selection, name='login_selection'),
    path('login/customer/', views.customer_login, name='customer_login'),
    path('login/staff/', views.staff_login, name='staff_login'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('home/', views.customer_home, name='customer_home'),
    path('orders/', views.customer_orders, name='customer_orders'),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('spending/', views.spending_dashboard, name='spending_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('logout/customer/', views.customer_logout_view, name='customer_logout'),
    path('delete/', views.delete_account_view, name='account_delete'),
    path('register/staff/', views.admin_register, name='admin_register'),
]
