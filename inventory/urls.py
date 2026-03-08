from django.urls import path
from . import views

urlpatterns = [
    path('scanner/', views.scanner_view, name='scanner'),
    path('gatepass/', views.gatepass_view, name='gatepass'),
    path('low-stock/', views.low_stock_items, name='low_stock_items'),
]
