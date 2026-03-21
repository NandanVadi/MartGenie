from django.urls import path
from . import views

urlpatterns = [
    path(
        'api/catalog/<str:store_code>/',
        views.get_products,
        name='get_inventory_products'
    ),
    path(
        'manager/',
        views.inventory_manager,
        name='inventory_manager'
    ),
    path(
        'api/inventory/',
        views.inventory_api,
        name='inventory_api'
    ),
    path(
        'api/barcode-lookup/<str:barcode>/',
        views.barcode_lookup,
        name='barcode_lookup'
    ),
]
