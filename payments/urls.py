from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_view, name='payment'),
    path('create/', views.create_order, name='create_order'),
    path('razorpay/create/', views.create_razorpay_order, name='create_razorpay_order'),
    path('razorpay/verify/', views.verify_payment, name='verify_razorpay_payment'),
]
