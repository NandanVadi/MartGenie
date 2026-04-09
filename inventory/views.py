from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import InventoryItem
from django.db import models

@login_required
def scanner_view(request):
    store_code = request.session.get('store_code', '')
    return render(request, 'Scanner.html', {'store_code': store_code})

@login_required
def exit_store_view(request):
    if 'store_code' in request.session:
        del request.session['store_code']
    return redirect('customer_home')

@login_required
def gatepass_view(request):
    return render(request, 'GatePass.html')

@login_required
def low_stock_items(request):
    """
    API endpoint to fetch items whose quantity is below their low_stock_threshold.
    """
    selected_store_id = request.session.get('admin_selected_store', 'all')
    
    low_stock = InventoryItem.objects.select_related('product', 'store').filter(
        quantity__lt=models.F('low_stock_threshold'),
        store__admin=request.user
    )

    if selected_store_id != 'all':
        try:
            low_stock = low_stock.filter(store_id=int(selected_store_id))
        except ValueError:
            pass

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
