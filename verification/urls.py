from django.urls import path
from . import views

urlpatterns = [
    path('security/', views.security_dashboard, name='security_dashboard'),
    path('security/login/', views.security_login, name='security_login'),
    path('security/login/submit/', views.security_login_post, name='security_login_post'),
    path('verify-pass/', views.verify_pass, name='verify_pass'),
]
