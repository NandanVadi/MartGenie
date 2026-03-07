from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from billing.models import Order, OrderItem
from core.models import Store
import json
from django.views.decorators.csrf import csrf_exempt

@login_required
def payment_view(request):
    return render(request, 'Payment.html')

from django.db import transaction
from products.models import Product
from inventory.models import InventoryItem
from notifications.models import Notification

@csrf_exempt
@login_required
def create_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user
            
            # Get Store
            store_code = request.session.get('store_code')
            store = None
            if store_code:
                store = Store.objects.filter(store_code=store_code).first()
            if not store:
                store = Store.objects.first() # Fallback to first available store for demo

            with transaction.atomic():
                # Create Order
                order = Order.objects.create(
                    user=user,
                    store=store,
                    order_id=data.get('orderId'),
                    total_amount=data.get('total'),
                    status='COMPLETED',
                    qr_data=data.get('qrData')
                )
                
                # Create Order Items and Update Inventory
                for item in data.get('items', []):
                    barcode = item.get('id')
                    qty = int(item.get('quantity', 0))
                    
                    # Inventory Logic
                    if store and barcode:
                        inventory_item = InventoryItem.objects.filter(
                            store=store, 
                            product__barcode=barcode
                        ).select_for_update().first()
                        
                        if inventory_item:
                            if inventory_item.quantity >= qty:
                                inventory_item.quantity -= qty
                            else:
                                # Allow going negative or limit to 0? Let's limit to 0 for now to avoid confusion
                                # Real world would be strict.
                                inventory_item.quantity = 0 
                                # Maybe notify admin about discrepancy?
                            
                            inventory_item.save()
                            
                            if inventory_item.quantity <= inventory_item.low_stock_threshold:
                                Notification.objects.create(
                                    message=f"Low Stock Alert: {inventory_item.product.name} (Qty: {inventory_item.quantity}) in {store.name}",
                                    notification_type='LOW_STOCK'
                                )

                    OrderItem.objects.create(
                        order=order,
                        product_name=item.get('name'),
                        product_id=barcode,
                        quantity=qty,
                        price=item.get('price')
                    )
                
            return JsonResponse({'status': 'success', 'order_id': order.order_id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
