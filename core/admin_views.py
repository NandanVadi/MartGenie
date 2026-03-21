from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from core.models import Store
from accounts.models import CustomUser, SecurityProfile
import traceback

@login_required
def admin_management(request):
    """
    Renders the unified admin management dashboard.
    Only allows users with ADMIN role.
    """
    if request.user.role != 'ADMIN':
        return redirect('dashboard')
        
    stores = Store.objects.filter(admin=request.user).order_by('name')
    return render(request, 'AdminManagement.html', {'stores': stores})

@login_required
@require_POST
@csrf_exempt
def add_store_api(request):
    if request.user.role != 'ADMIN':
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
        
    try:
        name = request.POST.get('name', '').strip()
        store_code = request.POST.get('store_code', '').strip().upper()
        location = request.POST.get('location', '').strip()
        
        if not name or not store_code:
            return JsonResponse({'status': 'error', 'message': 'Store name and code are required'})
            
        if Store.objects.filter(store_code=store_code).exists():
            return JsonResponse({'status': 'error', 'message': f'Store code {store_code} already exists'})
            
        Store.objects.create(
            name=name,
            store_code=store_code,
            address=location,
            admin=request.user
        )
        return JsonResponse({'status': 'success', 'message': 'Store added successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
@require_POST
@csrf_exempt
def create_security_api(request):
    if request.user.role != 'ADMIN':
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
        
    try:
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        phone_number = request.POST.get('phone_number', '').strip()
        
        store_id = request.POST.get('store_id')
        employee_id = request.POST.get('employee_id', '').strip()
        shift_start = request.POST.get('shift_start')
        shift_end = request.POST.get('shift_end')
        
        if not username or not password or not store_id or not employee_id:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})
            
        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse({'status': 'error', 'message': 'Username already taken'})
            
        if SecurityProfile.objects.filter(employee_id=employee_id).exists():
            return JsonResponse({'status': 'error', 'message': 'Employee ID already in use'})
            
        store = Store.objects.get(id=store_id, admin=request.user)
        
        # Create User
        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            phone_number=phone_number,
            role='SECURITY',
            is_staff=True
        )
        
        # Create Security Profile
        SecurityProfile.objects.create(
            user=user,
            store=store,
            employee_id=employee_id,
            shift_start=shift_start if shift_start else None,
            shift_end=shift_end if shift_end else None
        )
        
        return JsonResponse({'status': 'success', 'message': 'Security guard created and assigned successfully'})
    except Store.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Selected store does not exist'})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': 'Failed to create security account'})
