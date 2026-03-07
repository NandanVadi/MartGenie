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
                return render(request, 'CustomerEntry.html', {'step': 'store'})
            elif action == 'verify_store':
                store_code = request.POST.get('store_code')
                
                # Lazy import to avoid circular dependency if any
                from core.models import Store
                
                if store_code and Store.objects.filter(store_code=store_code).exists():
                    request.session['store_code'] = store_code
                    return render(request, 'CustomerEntry.html', {'step': 'phone'})
                else:
                    messages.error(request, "Invalid Store Code. Please check and try again.")
                    return render(request, 'CustomerEntry.html', {'step': 'store'})
            elif action == 'get_otp':
                phone_number = request.POST.get('phone_number')
                if phone_number:
                    # Generate Mock OTP
                    otp = str(random.randint(1000, 9999))
                    request.session['otp'] = otp
                    request.session['phone_number'] = phone_number
                    print(f"------------\nYour OTP is: {otp}\n------------") # Mock SMS
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

        if entered_otp and session_otp and entered_otp == session_otp:
            # Create or Get User
            user, created = CustomUser.objects.get_or_create(
                phone_number=phone_number,
                defaults={'username': phone_number, 'role': 'CUSTOMER'}
            )
            login(request, user)
            request.session.pop('otp', None) # Safe cleanup
            return redirect('customer_profile') 
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
            elif user.role == 'SECURITY':
                login(request, user)
                return redirect('security_dashboard') # Security Dashboard
            else:
                return render(request, 'loginpage.html', {'error': 'Access Denied. Staff only.'})
        else:
            return render(request, 'loginpage.html', {'error': 'Invalid Credentials'})
            
    return render(request, 'loginpage.html')

def logout_view(request):
    logout(request)
    return redirect('login_selection')

