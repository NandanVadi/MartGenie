from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_view, name='payment'),
    path('create/', views.create_order, name='create_order'),
]
