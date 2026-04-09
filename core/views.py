from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F
from django.utils import timezone
import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

def home(request):
    """
    Renders the landing page for the MartGenie application.
    """
    return render(request, 'Home.html')

@login_required
def cart_view(request):
    """
    Renders the customer cart page.
    """
    store_code = request.session.get('store_code')
    return render(request, 'Cart.html', {'store_code': store_code})

@login_required
def dashboard(request):
    """
    Renders the admin dashboard with sales statistics, charts, and recent orders.
    Filters data based on the requested time period.
    """
    # Enforce Store creation for admins
    if request.user.role == 'ADMIN':
        from core.models import Store
        if not Store.objects.filter(admin=request.user).exists():
            return redirect('admin_management')
    
    from billing.models import Order, OrderItem, GatePassLog
    from products.models import Product
    from inventory.models import InventoryItem
    from notifications.models import Notification

    # Filter for today for some stats
    today = timezone.localtime(timezone.now()).date()
    
    # Get filter parameters
    filter_type = request.GET.get('filter', 'today')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # Default range (Today)
    start_date = today
    end_date = today

    if filter_type == 'today':
        start_date = today
        end_date = today
    elif filter_type == 'yesterday':
        start_date = today - datetime.timedelta(days=1)
        end_date = start_date
    elif filter_type == 'week': # This Week (Mon-Sun)
        start_date = today - datetime.timedelta(days=today.weekday())
        end_date = today
    elif filter_type == 'month': # This Month
        start_date = today.replace(day=1)
        end_date = today
    elif filter_type == 'year': # This Year
        start_date = today.replace(month=1, day=1)
        end_date = today
    elif filter_type == 'all':
        start_date = None
        end_date = None
    elif filter_type == 'custom' and start_date_str and end_date_str:
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass # Fallback to today

    # Dynamic Chart Title
    chart_title = "Sales This Week"
    if filter_type == 'today':
        chart_title = "Sales Today"
    elif filter_type == 'yesterday':
        chart_title = "Sales Yesterday"
    elif filter_type == 'week':
        chart_title = "Sales This Week"
    elif filter_type == 'month':
        chart_title = "Sales This Month"
    elif filter_type == 'year':
        chart_title = "Sales This Year"
    elif filter_type == 'all':
        chart_title = "All Time Sales"
    elif filter_type == 'custom':
        chart_title = f"Sales from {start_date} to {end_date}"

    # Filter Label for KPI Cards
    filter_labels = {
        'today': 'Today',
        'yesterday': 'Yesterday',
        'week': 'This Week',
        'month': 'This Month',
        'year': 'This Year',
        'all': 'All Time',
        'custom': 'Custom Range'
    }
    filter_label = filter_labels.get(filter_type, 'Today')

    # Store Filtering Coordination
    stores = Store.objects.filter(admin=request.user).order_by('name')
    
    # Priority: 1. URL Param, 2. Session, 3. Default 'all'
    selected_store = request.GET.get('store')
    if selected_store:
        request.session['admin_selected_store'] = selected_store
    else:
        selected_store = request.session.get('admin_selected_store', 'all')
    
    current_store = None
    if selected_store != 'all':
        current_store = stores.filter(id=selected_store).first()
    if not current_store and stores.exists() and selected_store != 'all':
        # Fallback if the saved ID is invalid
        current_store = stores.first()
        selected_store = str(current_store.id)
        request.session['admin_selected_store'] = selected_store

    # Base Orders Query (Multi-tenant)
    orders_query = Order.objects.filter(store__admin=request.user)
    
    if selected_store != 'all':
        try:
             orders_query = orders_query.filter(store_id=int(selected_store))
        except ValueError:
             pass 
             
    if start_date and end_date:
        orders_query = orders_query.filter(created_at__date__range=[start_date, end_date])
    
    # Aggregates
    total_revenue = orders_query.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    unique_customers = orders_query.values('user').distinct().count()
    
    # Items sold logic
    items_sold = OrderItem.objects.filter(order__in=orders_query).aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    # Gate passes used in this period
    gate_pass_used_count = GatePassLog.objects.filter(order__in=orders_query, status='APPROVED').count()
    
    # Recent orders
    recent_orders = orders_query.select_related('user').prefetch_related('items').order_by('-created_at')[:5]
    
    # Product Catalog
    products_query = Product.objects.filter(inventory_items__store__admin=request.user)
    if selected_store != 'all':
        try:
            products_query = products_query.filter(inventory_items__store_id=int(selected_store))
        except ValueError:
            pass
    products = products_query.distinct()

    # Total products and low stock
    inventory_query = InventoryItem.objects.filter(store__admin=request.user)
    if selected_store != 'all':
        try:
            inventory_query = inventory_query.filter(store_id=int(selected_store))
        except ValueError:
            pass
    total_products = inventory_query.count()
    low_stock_count = sum(1 for item in inventory_query if item.is_low_stock())
    
    # Today-specific stats for KPI cards
    today_orders = Order.objects.filter(store__admin=request.user, created_at__date=today)
    if selected_store != 'all':
        try:
            today_orders = today_orders.filter(store_id=int(selected_store))
        except ValueError:
            pass
    today_revenue = today_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    today_order_count = today_orders.count()
    today_pending = today_orders.filter(status='PENDING').count()
    
    # Yesterday for comparison
    yesterday = today - datetime.timedelta(days=1)
    yesterday_orders = Order.objects.filter(store__admin=request.user, created_at__date=yesterday)
    if selected_store != 'all':
        try:
            yesterday_orders = yesterday_orders.filter(store_id=int(selected_store))
        except ValueError:
            pass
    yesterday_revenue = yesterday_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    if yesterday_revenue > 0:
        revenue_change = round(((float(today_revenue) - float(yesterday_revenue)) / float(yesterday_revenue)) * 100)
    else:
        revenue_change = 100 if today_revenue > 0 else 0
    
    today_gate_passes = GatePassLog.objects.filter(order__store__admin=request.user, verified_at__date=today, status='APPROVED')
    if selected_store != 'all':
        try:
            today_gate_passes = today_gate_passes.filter(order__store_id=int(selected_store))
        except ValueError:
            pass
    today_gate_pass_count = today_gate_passes.count()

    # Chart Data Logic
    from django.db.models.functions import TruncDate, TruncHour
    chart_labels = []
    chart_values = []
    
    is_single_day = (start_date and end_date and start_date == end_date)
    
    if is_single_day:
        data = orders_query.annotate(hour=TruncHour('created_at')).values('hour').annotate(total=Sum('total_amount')).order_by('hour')
        hourly_data = {h: 0 for h in range(24)}
        for entry in data:
            if entry['hour']:
                h = timezone.localtime(entry['hour']).hour
                hourly_data[h] = float(entry['total'])
        chart_labels = [f"{h:02d}:00" for h in range(24)]
        chart_values = [hourly_data[h] for h in range(24)]
    else:
        data = orders_query.annotate(day=TruncDate('created_at')).values('day').annotate(total=Sum('total_amount')).order_by('day')
        date_map = {entry['day']: float(entry['total']) for entry in data if entry['day']}
        if start_date and end_date:
            delta = end_date - start_date
            for i in range(delta.days + 1):
                d = start_date + datetime.timedelta(days=i)
                chart_labels.append(d.strftime('%b %d'))
                chart_values.append(date_map.get(d, 0))
        else:
            for entry in data:
                if entry['day']:
                    chart_labels.append(entry['day'].strftime('%b %d, %Y'))
                    chart_values.append(float(entry['total']))

    # Notifications
    unread_notifications_query = Notification.objects.filter(is_read=False, store__admin=request.user)
    if selected_store != 'all':
        try:
            unread_notifications_query = unread_notifications_query.filter(store_id=int(selected_store))
        except ValueError:
            pass
    unread_notifications = unread_notifications_query.order_by('-created_at')[:10]
    unread_count = unread_notifications_query.count()

    context = {
        'total_revenue': total_revenue,
        'unique_customers': unique_customers,
        'items_sold': items_sold,
        'order_count': orders_query.count(),
        'gate_pass_used_count': gate_pass_used_count,
        'recent_orders': recent_orders,
        'products': products,
        'today_date': today,
        'avg_order_value': round(total_revenue / orders_query.count(), 2) if orders_query.count() > 0 else 0,
        'today_revenue': today_revenue,
        'today_order_count': today_order_count,
        'today_pending': today_pending,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'today_gate_pass_count': today_gate_pass_count,
        'revenue_change': revenue_change,
        'filter_type': filter_type,
        'start_date': start_date.strftime('%Y-%m-%d') if start_date else '',
        'end_date': end_date.strftime('%Y-%m-%d') if end_date else '',
        'stores': stores,
        'selected_store': selected_store,
        'chart_title': chart_title,
        'filter_label': filter_label,
        'display_revenue': total_revenue,
        'display_orders': orders_query.count(),
        'display_gate_passes': gate_pass_used_count,
        'current_store': current_store,
        'unread_notifications': unread_notifications,
        'unread_count': unread_count,
        'chart_labels': chart_labels,
        'chart_values': chart_values,
    }
    return render(request, 'DashBoard.html', context)

@login_required
@require_POST
@csrf_exempt
def mark_notifications_read(request):
    from notifications.models import Notification
    Notification.objects.filter(is_read=False, store__admin=request.user).update(is_read=True)
    return JsonResponse({'status': 'success', 'message': 'Notifications marked as read'})

@login_required
def sales_ledger(request):
    if request.user.role != 'ADMIN':
        return render(request, 'Home.html', {'error': 'Unauthorized'})
    from billing.models import Order
    
    # Session Persistence
    selected_store = request.session.get('admin_selected_store', 'all')
    
    orders = Order.objects.filter(store__admin=request.user).select_related('user', 'store').order_by('-created_at')
    
    if selected_store != 'all':
        try:
            orders = orders.filter(store_id=int(selected_store))
        except ValueError:
            pass
            
    return render(request, 'Sales.html', {
        'orders': orders,
        'selected_store': selected_store,
        'stores': Store.objects.filter(admin=request.user).order_by('name')
    })

@login_required
def customers_crm(request):
    if request.user.role != 'ADMIN':
        return render(request, 'Home.html', {'error': 'Unauthorized'})
    from accounts.models import CustomUser
    
    # Session Persistence
    selected_store = request.session.get('admin_selected_store', 'all')
    
    # Base Query: Customers who have shopped at any store managed by this admin
    customers_query = CustomUser.objects.filter(role='CUSTOMER')
    
    if selected_store != 'all':
        try:
            # Filter customers who have orders in the specific store
            customers_query = customers_query.filter(orders__store_id=int(selected_store)).distinct()
            customers = customers_query.annotate(
                total_spent=Sum('orders__total_amount', filter=Q(orders__store_id=int(selected_store)))
            ).order_by('-total_spent')
        except ValueError:
            customers = customers_query.annotate(total_spent=Sum('orders__total_amount')).order_by('-total_spent')
    else:
        # Show all customers for all admin stores
        customers_query = customers_query.filter(orders__store__admin=request.user).distinct()
        customers = customers_query.annotate(
            total_spent=Sum('orders__total_amount')
        ).order_by('-total_spent')
        
    return render(request, 'Customers.html', {
        'customers': customers,
        'selected_store': selected_store,
        'stores': Store.objects.filter(admin=request.user).order_by('name')
    })
