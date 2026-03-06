from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    """
    Renders the landing page for the MartGenie application.
    """
    return render(request, 'Home.html')

@login_required
def dashboard(request):
    """
    Renders the admin dashboard with sales statistics, charts, and recent orders.
    Filters data based on the requested time period.
    """
    # Imports inside view to avoid circular imports if any, though top-level is better if safe
    from billing.models import Order, OrderItem, GatePassLog
    from products.models import Product
    from django.db.models import Sum, Count, F
    from django.utils import timezone
    import datetime

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

    # Filter Orders
    orders_query = Order.objects.all()
    if start_date and end_date:
        # Filter by range (inclusive)
        # For DateTimeField, end_date needs to cover the whole day, so usually < end_date + 1 day or __date__range
        orders_query = orders_query.filter(created_at__date__range=[start_date, end_date])
    
    # Aggregates
    total_revenue = orders_query.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    unique_customers = orders_query.values('user').distinct().count()
    
    # Items sold logic
    items_sold = OrderItem.objects.filter(order__in=orders_query).aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    # Gate passes used in this period
    gate_pass_used_count = GatePassLog.objects.filter(order__in=orders_query, status='APPROVED').count()
    
    # Recent orders (fetch last 5 from the filtered set or just global recent? usually context specific)
    # Let's show recent orders from the *selected period* to be consistent
    recent_orders = orders_query.select_related('user').prefetch_related('items').order_by('-created_at')[:5]
    
    # Product Catalog (Always all)
    products = Product.objects.all()
    
    context = {
        'total_revenue': total_revenue,
        'unique_customers': unique_customers,
        'items_sold': items_sold,
        'order_count': orders_query.count(), # Renamed from today_order_count to be generic
        'gate_pass_used_count': gate_pass_used_count,
        'recent_orders': recent_orders,
        'products': products,
        'today_date': today,
        'avg_order_value': round(total_revenue / orders_query.count(), 2) if orders_query.count() > 0 else 0,
        
        'filter_type': filter_type,
        'start_date': start_date.strftime('%Y-%m-%d') if start_date else '',
        'end_date': end_date.strftime('%Y-%m-%d') if end_date else '',
    }

    # Chart Data Logic
    from django.db.models.functions import TruncDate, TruncHour
    
    chart_query = orders_query
    chart_labels = []
    chart_values = []
    
    # If range is 1 day (or Today/Yesterday), group by Hour
    is_single_day = False
    if start_date and end_date and start_date == end_date:
        is_single_day = True
    
    if is_single_day:
        # Group by Hour
        data = chart_query.annotate(hour=TruncHour('created_at')).values('hour').annotate(total=Sum('total_amount')).order_by('hour')
        
        # Initialize dictionary for 24 hours
        hourly_data = {h: 0 for h in range(24)}
        for entry in data:
            if entry['hour']:
                # entry['hour'] is a datetime object
                h = timezone.localtime(entry['hour']).hour
                hourly_data[h] = float(entry['total'])
        
        chart_labels = [f"{h:02d}:00" for h in range(24)]
        chart_values = [hourly_data[h] for h in range(24)]
        
    else:
        # Group by Date
        data = chart_query.annotate(day=TruncDate('created_at')).values('day').annotate(total=Sum('total_amount')).order_by('day')
        
        # For ranges, we might want to fill gaps, but for now let's just show days with sales or raw timeline
        # Filling gaps is better for UI.
        
        date_map = {}
        for entry in data:
            if entry['day']:
                 date_map[entry['day']] = float(entry['total'])
        
        # Generate range of dates if start/end exist, otherwise just use data points
        if start_date and end_date:
            delta = end_date - start_date
            for i in range(delta.days + 1):
                d = start_date + datetime.timedelta(days=i)
                chart_labels.append(d.strftime('%b %d'))
                chart_values.append(date_map.get(d, 0))
        else:
            # All time - just use the dates we have
            for entry in data:
                if entry['day']:
                    chart_labels.append(entry['day'].strftime('%b %d, %Y'))
                    chart_values.append(float(entry['total']))
    
    context['chart_labels'] = chart_labels
    context['chart_values'] = chart_values

    return render(request, 'DashBoard.html', context)
