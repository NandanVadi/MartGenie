from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from billing.models import Order, OrderItem
from core.models import Store
import json
import hmac
import hashlib
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import razorpay

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def payment_view(request):
    store_code = request.session.get('store_code')
    return render(request, 'Payment.html', {
        'store_code': store_code,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    })

from django.db import transaction
from products.models import Product
from inventory.models import InventoryItem
from notifications.models import Notification

@csrf_exempt
@login_required
def create_razorpay_order(request):
    """Create a Razorpay order and return order_id to frontend."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = data.get('amount')  # Amount in rupees from frontend

            if not amount or float(amount) <= 0:
                return JsonResponse({'status': 'error', 'message': 'Invalid amount'}, status=400)

            # Razorpay expects amount in paise (1 INR = 100 paise)
            amount_in_paise = int(float(amount) * 100)

            razorpay_order = razorpay_client.order.create({
                'amount': amount_in_paise,
                'currency': 'INR',
                'payment_capture': 1,  # Auto-capture payment
            })

            return JsonResponse({
                'status': 'success',
                'order_id': razorpay_order['id'],
                'amount': amount_in_paise,
                'currency': 'INR',
                'key_id': settings.RAZORPAY_KEY_ID,
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


@csrf_exempt
@login_required
def verify_payment(request):
    """Verify Razorpay payment signature and create order in DB."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Extract Razorpay payment details
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_signature = data.get('razorpay_signature')

            # Verify signature using HMAC SHA256
            message = f"{razorpay_order_id}|{razorpay_payment_id}"
            generated_signature = hmac.new(
                settings.RAZORPAY_KEY_SECRET.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            if generated_signature != razorpay_signature:
                return JsonResponse({'status': 'error', 'message': 'Payment verification failed. Invalid signature.'}, status=400)

            # --- Payment is verified, now create the order ---
            user = request.user
            store_code = request.session.get('store_code')
            if not store_code:
                return JsonResponse({'status': 'error', 'message': 'Store session lost. Please scan entry QR.'}, status=400)

            store = Store.objects.filter(store_code=store_code).first()
            if not store:
                return JsonResponse({'status': 'error', 'message': 'Invalid store session.'}, status=400)

            cart_items = data.get('items', [])
            order_id_str = data.get('orderId')
            qr_data = data.get('qrData')

            with transaction.atomic():
                calculated_total = 0
                items_to_create = []

                for item in cart_items:
                    barcode = item.get('id')
                    qty = int(item.get('quantity', 0))

                    if qty <= 0:
                        continue

                    inventory_item = InventoryItem.objects.filter(
                        store=store,
                        product__barcode=barcode
                    ).select_for_update().first()

                    if not inventory_item:
                        return JsonResponse({'status': 'error', 'message': f'Product {item.get("name")} not found in this store.'}, status=400)

                    if inventory_item.quantity < qty:
                        return JsonResponse({'status': 'error', 'message': f'Insufficient stock for {inventory_item.product.name}.'}, status=400)

                    # Stock is deducted, logic move to signals for centralization
                    inventory_item.quantity -= qty
                    inventory_item.save()

                    item_price = inventory_item.product.price
                    calculated_total += item_price * qty

                    items_to_create.append({
                        'product_name': inventory_item.product.name,
                        'product_id': barcode,
                        'quantity': qty,
                        'price': item_price
                    })

                # Create Order with Razorpay payment info
                order = Order.objects.create(
                    user=user,
                    store=store,
                    order_id=order_id_str,
                    total_amount=calculated_total,
                    status='COMPLETED',
                    qr_data=qr_data
                )

                for item_data in items_to_create:
                    OrderItem.objects.create(
                        order=order,
                        product_name=item_data['product_name'],
                        product_id=item_data['product_id'],
                        quantity=item_data['quantity'],
                        price=item_data['price']
                    )

            return JsonResponse({
                'status': 'success',
                'order_id': order.order_id,
                'message': 'Payment verified and order created.'
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


# Keep legacy create_order for backward compatibility
@csrf_exempt
@login_required
def create_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user

            store_code = request.session.get('store_code')
            if not store_code:
                return JsonResponse({'status': 'error', 'message': 'Store session lost. Please scan entry QR.'}, status=400)

            store = Store.objects.filter(store_code=store_code).first()
            if not store:
                return JsonResponse({'status': 'error', 'message': 'Invalid store session.'}, status=400)

            with transaction.atomic():
                calculated_total = 0
                items_to_create = []

                for item in data.get('items', []):
                    barcode = item.get('id')
                    qty = int(item.get('quantity', 0))

                    if qty <= 0:
                        continue

                    inventory_item = InventoryItem.objects.filter(
                        store=store,
                        product__barcode=barcode
                    ).select_for_update().first()

                    if not inventory_item:
                        return JsonResponse({'status': 'error', 'message': f'Product {item.get("name")} not found in this store.'}, status=400)

                    if inventory_item.quantity < qty:
                        return JsonResponse({'status': 'error', 'message': f'Insufficient stock for {inventory_item.product.name}.'}, status=400)

                    inventory_item.quantity -= qty
                    inventory_item.save()

                    item_price = inventory_item.product.price
                    calculated_total += item_price * qty

                    items_to_create.append({
                        'product_name': inventory_item.product.name,
                        'product_id': barcode,
                        'quantity': qty,
                        'price': item_price
                    })

                order = Order.objects.create(
                    user=user,
                    store=store,
                    order_id=data.get('orderId'),
                    total_amount=calculated_total,
                    status='COMPLETED',
                    qr_data=data.get('qrData')
                )

                for item_data in items_to_create:
                    OrderItem.objects.create(
                        order=order,
                        product_name=item_data['product_name'],
                        product_id=item_data['product_id'],
                        quantity=item_data['quantity'],
                        price=item_data['price']
                    )

            return JsonResponse({'status': 'success', 'order_id': order.order_id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
