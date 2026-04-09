from django.urls import path
from . import views

urlpatterns = [
    path('scanner/', views.scanner_view, name='scanner'),
    path('exit-store/', views.exit_store_view, name='exit_store'),
    path('gatepass/', views.gatepass_view, name='gatepass'),
    path('low-stock/', views.low_stock_items, name='low_stock_items'),
]
