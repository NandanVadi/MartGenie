from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
]
