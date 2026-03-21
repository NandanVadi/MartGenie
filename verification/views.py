from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from billing.models import Order, GatePassLog
import json # Import json for parsing request body

@login_required
def security_dashboard(request):
    if request.user.role != 'SECURITY':
        return render(request, 'loginpage.html', {'error': 'Access Denied.'})
    return render(request, 'SecurityGuard.html')

def security_login(request):
    return render(request, 'Security.html')

@csrf_exempt
def security_login_post(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        from django.contrib.auth import authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.role == 'SECURITY':
                from django.contrib.auth import login
                login(request, user)
                return redirect('security_dashboard')
            else:
                return render(request, 'Security.html', {'error': 'Access Denied. This portal is for Security Guards only.'})
        else:
            return render(request, 'Security.html', {'error': 'Invalid username or password.'})
    return redirect('security_login')

@csrf_exempt
@login_required
def verify_pass(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action', 'fetch') # 'fetch' or 'decide'
            qr_data = data.get('qr_data')
            
            # Logic to parse QR data: "MARTGENIE:{orderId}:{timestamp}"
            order_id = qr_data
            if "MARTGENIE:" in qr_data:
                parts = qr_data.split(':')
                if len(parts) >= 2:
                    order_id = parts[1]

            # 1. Check if Order exists
            order = Order.objects.filter(order_id=order_id).first()
            if not order:
                 return JsonResponse({'status': 'invalid', 'message': 'Order not found.'})

            # Check Store Authorization
            if request.user.role == 'SECURITY':
                if not hasattr(request.user, 'security_profile') or order.store != request.user.security_profile.store:
                    return JsonResponse({'status': 'invalid', 'message': f'Unauthorized: This bill belongs to {order.store.name}, not your assigned store.'})

            # Check if already verified/used
            existing_log = GatePassLog.objects.filter(order=order, status='APPROVED').first()
            
            if action == 'fetch':
                if existing_log:
                    return JsonResponse({
                        'status': 'used', 
                        'message': 'Gate Pass already used.',
                        'time': existing_log.verified_at.isoformat(),
                        'order_id': order.order_id,
                        'amount': order.total_amount,
                         # Return items even if used, for reference
                        'items': list(order.items.values('product_name', 'quantity')) 
                    })
                
                # Valid, not used yet. Return details for review.
                return JsonResponse({
                    'status': 'review', # New status for frontend
                    'order_id': order.order_id,
                    'amount': order.total_amount,
                    'items': list(order.items.values('product_name', 'quantity'))
                })

            elif action == 'decide':
                decision = data.get('decision') # 'APPROVED' or 'REJECTED'
                
                if decision == 'APPROVED':
                    if existing_log:
                         return JsonResponse({'status': 'used', 'message': 'Already used'})
                    
                    GatePassLog.objects.create(guard=request.user, order=order, status='APPROVED')
                    return JsonResponse({'status': 'approved'})
                
                elif decision == 'REJECTED':
                    GatePassLog.objects.create(guard=request.user, order=order, status='REJECTED', remarks=data.get('remarks', 'Manual Rejection'))
                    return JsonResponse({'status': 'rejected'})

        except Exception as e:
             return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
