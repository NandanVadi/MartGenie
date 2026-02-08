from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import CustomUser
from django.contrib import messages
import random

def login_selection(request):
    return render(request, 'accounts/login_selection.html')

def customer_login(request):
    if request.method == 'POST':
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
    return render(request, 'accounts/login_customer.html')

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        phone_number = request.session.get('phone_number')

        if entered_otp == session_otp:
            # Create or Get User
            user, created = CustomUser.objects.get_or_create(
                phone_number=phone_number,
                defaults={'username': phone_number, 'role': 'CUSTOMER'}
            )
            login(request, user)
            del request.session['otp'] # Cleanup
            return redirect('home')
            messages.error(request, "Invalid OTP. Please try again.")
    return render(request, 'accounts/verify_otp.html')

def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate User
        from django.contrib.auth import authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.role in ['ADMIN', 'SECURITY']:
                login(request, user)
                return redirect('home') # Redirect to dashboard later
            else:
                return render(request, 'accounts/login_staff.html', {'error': 'Access Denied. Staff only.'})
        else:
            return render(request, 'accounts/login_staff.html', {'error': 'Invalid Credentials'})
            
    return render(request, 'accounts/login_staff.html')

