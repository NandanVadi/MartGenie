from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .models import CustomUser
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import random

def login_selection(request):
    return render(request, 'loginpage.html')

@csrf_exempt
def customer_login(request):
    step = request.GET.get('step', 'welcome')
    
    if request.method == 'POST':
        if 'action' in request.POST:
            action = request.POST.get('action')
            if action == 'start_shopping':
                return render(request, 'CustomerEntry.html', {'step': 'phone'})
            elif action == 'get_otp':
                phone_number = request.POST.get('phone_number')
                name = request.POST.get('name', '')
                if phone_number:
                    # Generate Mock OTP
                    otp = str(random.randint(1000, 9999))
                    request.session['otp'] = otp
                    request.session['phone_number'] = phone_number
                    request.session['name'] = name
                    return redirect('verify_otp')
                else:
                    messages.error(request, "Please enter a valid phone number.")
                    return render(request, 'CustomerEntry.html', {'step': 'phone'})
                    
    return render(request, 'CustomerEntry.html', {'step': step})

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        phone_number = request.session.get('phone_number')
        name = request.session.get('name', '')

        if entered_otp and session_otp and entered_otp == session_otp:
            # Create or Get User
            user, created = CustomUser.objects.get_or_create(
                phone_number=phone_number,
                defaults={'username': phone_number, 'role': 'CUSTOMER', 'first_name': name}
            )
            
            # If the user already exists but the name they just entered is different, update it
            if not created and name and user.first_name != name:
                user.first_name = name
                user.save(update_fields=['first_name'])
                
            login(request, user)

            request.session.pop('otp', None) # Safe cleanup
            return redirect('customer_home') 
        else:
            messages.error(request, "Invalid OTP. Please try again.")
    
    otp = request.session.get('otp')
    return render(request, 'CustomerEntry.html', {'step': 'otp', 'debug_otp': otp})

@login_required
def customer_profile(request):
    if request.user.role != 'CUSTOMER':
        return redirect('home')
        
    # Lazy import to avoid circular dependency
    from billing.models import Order
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/profile.html', {'orders': orders})

@login_required
def delete_account_view(request):
    """
    Permanently deletes the current user's account and logs them out.
    """
    if request.user.role != 'CUSTOMER':
        return redirect('customer_home')

    user = request.user
    user.delete()
    logout(request)
    messages.success(request, "Your account has been permanently deleted. We're sorry to see you go!")
    return redirect('customer_login')

@login_required
def spending_dashboard(request):
    if request.user.role != 'CUSTOMER':
        return redirect('home')
    
    from billing.models import Order, OrderItem
    from django.db.models import Sum, Count, Avg, F
    from django.db.models.functions import TruncMonth
    import json
    from datetime import datetime, timedelta
    
    # All orders for this customer
    orders = Order.objects.filter(user=request.user, status='COMPLETED')
    
    # Lifetime stats
    lifetime_stats = orders.aggregate(
        total_spent=Sum('total_amount'),
        total_orders=Count('id'),
    )
    total_spent = lifetime_stats['total_spent'] or 0
    total_orders = lifetime_stats['total_orders'] or 0
    stores_visited = orders.values('store').distinct().count()
    
    # Per-store breakdown
    store_data = orders.values(
        'store__id', 'store__name', 'store__store_code'
    ).annotate(
        total_spent=Sum('total_amount'),
        order_count=Count('id'),
        avg_order=Avg('total_amount'),
    ).order_by('-total_spent')
    
    # Add last visit date and spending percentage
    store_analytics = []
    for s in store_data:
        last_order = orders.filter(store_id=s['store__id']).order_by('-created_at').first()
        pct = (float(s['total_spent']) / float(total_spent) * 100) if total_spent > 0 else 0
        store_analytics.append({
            'name': s['store__name'] or 'Unknown Store',
            'code': s['store__store_code'] or '',
            'total_spent': s['total_spent'],
            'order_count': s['order_count'],
            'avg_order': round(s['avg_order'], 2) if s['avg_order'] else 0,
            'last_visit': last_order.created_at if last_order else None,
            'percentage': round(pct, 1),
        })
    
    # Top products
    top_products = OrderItem.objects.filter(
        order__user=request.user, order__status='COMPLETED'
    ).values('product_name').annotate(
        times_bought=Sum('quantity'),
        total_spent=Sum(F('price') * F('quantity')),
    ).order_by('-times_bought')[:5]
    
    # Monthly spending (last 6 months)
    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_data = orders.filter(
        created_at__gte=six_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        spent=Sum('total_amount')
    ).order_by('month')
    
    monthly_labels = [m['month'].strftime('%b %Y') for m in monthly_data]
    monthly_values = [float(m['spent']) for m in monthly_data]
    
    context = {
        'total_spent': total_spent,
        'total_orders': total_orders,
        'stores_visited': stores_visited,
        'store_analytics': store_analytics,
        'top_products': top_products,
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_values': json.dumps(monthly_values),
    }
    return render(request, 'accounts/spending_dashboard.html', context)
@login_required
def customer_home(request):
    if request.user.role != 'CUSTOMER':
        return redirect('home')
        
    if request.method == 'POST' and request.POST.get('action') == 'verify_store':
        store_code = request.POST.get('store_code')
        from core.models import Store
        if store_code and Store.objects.filter(store_code=store_code).exists():
            request.session['store_code'] = store_code
            return redirect('scanner')
        else:
            messages.error(request, "Invalid Store QR Code. Please check and try again.")
            return redirect('customer_home')
    
    # Fetch active promotions and stores
    from core.models import Store, Promotion
    stores = Store.objects.filter(is_active=True).order_by('?')[:3]
    promotions = Promotion.objects.filter(is_active=True).order_by('-created_at')[:4]
    
    context = {
        'stores': stores,
        'promotions': promotions,
    }
    return render(request, 'accounts/customer_home.html', context)

@login_required
def customer_orders(request):
    if request.user.role != 'CUSTOMER':
        return redirect('home')
        
    from billing.models import Order
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'accounts/customer_orders.html', {'orders': orders})

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate User
        from django.contrib.auth import authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.role == 'ADMIN':
                login(request, user)
                return redirect('dashboard') # Admin Dashboard
            else:
                return render(request, 'loginpage.html', {'error': 'Access Denied. This portal is for Admin accounts only.'})
        else:
            return render(request, 'loginpage.html', {'error': 'Invalid Credentials'})
            
    return render(request, 'loginpage.html')

def logout_view(request):
    logout(request)
    return redirect('login_selection')

def customer_logout_view(request):
    logout(request)
    return redirect('customer_login')

@csrf_exempt
def admin_register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        phone_number = request.POST.get('phone_number', '').strip()
        
        if not username or not password:
            return render(request, 'admin_register.html', {'error': 'Username and password are required'})
            
        if not phone_number.isdigit() or len(phone_number) < 10:
            return render(request, 'admin_register.html', {'error': 'Please enter a valid numeric phone number (min 10 digits)'})
            
        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'admin_register.html', {'error': 'Username already taken'})
            
        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            phone_number=phone_number,
            role='ADMIN',
            is_staff=True
        )
        login(request, user)
        
        # Redirect to management so they can add a store immediately
        return redirect('admin_management')
        
    return render(request, 'admin_register.html')

