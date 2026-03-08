from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import InventoryItem
from django.db import models

@login_required
def scanner_view(request):
    store_code = request.session.get('store_code', 'MARTGENIE-STORE-001') # Default for now if missing
    return render(request, 'Scanner.html', {'store_code': store_code})

@login_required
def gatepass_view(request):
    return render(request, 'GatePass.html')

@login_required
def low_stock_items(request):
    """
    API endpoint to fetch items whose quantity is below their low_stock_threshold.
    """
    low_stock = InventoryItem.objects.select_related('product', 'store').filter(
        quantity__lt=models.F('low_stock_threshold')
    )

    data = []
    for item in low_stock:
        data.append({
            "product_name": item.product.name,
            "barcode": item.product.barcode,
            "store": item.store.name,
            "quantity": item.quantity,
            "threshold": item.low_stock_threshold
        })

    return JsonResponse({
        "count": len(data),
        "items": data
    })
