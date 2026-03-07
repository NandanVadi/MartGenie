from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_selection, name='login_selection'),
    path('login/customer/', views.customer_login, name='customer_login'),
    path('login/staff/', views.staff_login, name='staff_login'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('logout/', views.logout_view, name='logout'),
    path('logout/customer/', views.customer_logout_view, name='customer_logout'),
]
