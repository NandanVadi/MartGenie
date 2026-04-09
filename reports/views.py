import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from billing.models import OrderItem, Order
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta, datetime

@login_required
def reports_dashboard(request):
    # Enforce admin access
    if request.user.role != 'ADMIN':
        return render(request, 'Home.html', {'error': 'Unauthorized'})

    # Filtering Logic (Same as main dashboard)
    today = timezone.localtime(timezone.now()).date()
    filter_type = request.GET.get('filter', 'week')
    
    start_date = today
    end_date = today
    chart_period_label = "This Week"

    if filter_type == 'today':
        start_date = today
        end_date = today
        chart_period_label = "Today"
    elif filter_type == 'yesterday':
        start_date = today - timedelta(days=1)
        end_date = start_date
        chart_period_label = "Yesterday"
    elif filter_type == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = today
        chart_period_label = "This Week"
    elif filter_type == 'month':
        start_date = today.replace(day=1)
        end_date = today
        chart_period_label = "This Month"
    elif filter_type == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today
        chart_period_label = "This Year"
    elif filter_type == 'all':
        start_date = None
        end_date = None
        chart_period_label = "All Time"

    # Store Persistence
    stores = Store.objects.filter(admin=request.user).order_by('name')
    selected_store = request.session.get('admin_selected_store', 'all')
    
    current_store = None
    if selected_store != 'all':
        current_store = stores.filter(id=selected_store).first()

    # Base Queries
    orders_query = Order.objects.filter(store__admin=request.user)
    order_items_query = OrderItem.objects.filter(order__store__admin=request.user)

    if selected_store != 'all':
        try:
            orders_query = orders_query.filter(store_id=int(selected_store))
            order_items_query = order_items_query.filter(order__store_id=int(selected_store))
        except ValueError:
            pass

    if start_date and end_date:
        orders_query = orders_query.filter(created_at__date__range=[start_date, end_date])
        order_items_query = order_items_query.filter(order__created_at__date__range=[start_date, end_date])

    # Chart 1: Top 5 Bestselling Products
    top_products = order_items_query.values('product_name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]
    
    product_names = [item['product_name'] for item in top_products]
    quantities = [item['total_sold'] for item in top_products]

    if not product_names:
        product_names = ["No Data"]
        quantities = [0]

    plt.figure(figsize=(8, 4), facecolor='white')
    plt.barh(product_names, quantities, color='#10b981', align='center')
    plt.xlabel('Quantity Sold', color='#374151')
    plt.title(f'Top 5 Bestselling Products ({chart_period_label})', color='#374151', weight='bold')
    plt.gca().invert_yaxis()
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    buf.seek(0)
    top_products_chart = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()

    # Chart 2: Revenue Timeline
    # For timeline, we usually want to show a range even if filter is 1 day.
    # If filter is 'today' or 'yesterday', show hourly? Or just keep it as is.
    # User said "customizable", so let's make it respect the range.
    
    if filter_type in ['today', 'yesterday']:
        # Show last 24 hours or just the day
        dates = [start_date]
    elif filter_type == 'all':
        # Show all dates with sales
        date_data = orders_query.dates('created_at', 'day')
        dates = list(date_data) if date_data else [today]
    else:
        # Show range between start and end
        delta = (end_date - start_date).days
        dates = [start_date + timedelta(days=i) for i in range(delta + 1)]

    revenue_data = []
    for d in dates:
        daily_revenue = orders_query.filter(status='COMPLETED', created_at__date=d).aggregate(
            Sum('total_amount')
        )['total_amount__sum']
        revenue_data.append(float(daily_revenue or 0))

    date_labels = [d.strftime('%b %d') for d in dates]

    plt.figure(figsize=(8, 4), facecolor='white')
    plt.plot(date_labels, revenue_data, marker='o', color='#0f766e', linewidth=2, markersize=8)
    plt.xlabel('Date', color='#374151')
    plt.ylabel('Revenue (Rs)', color='#374151')
    plt.title(f'Revenue Timeline ({chart_period_label})', color='#374151', weight='bold')
    plt.grid(True, linestyle='--', alpha=0.5, color='#cbd5e1')
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png', bbox_inches='tight', transparent=True)
    buf2.seek(0)
    revenue_chart = base64.b64encode(buf2.getvalue()).decode('utf-8')
    plt.close()

    context = {
        'top_products_chart': top_products_chart,
        'revenue_chart': revenue_chart,
        'filter_type': filter_type,
        'chart_period_label': chart_period_label,
        'selected_store': selected_store,
        'current_store': current_store,
        'stores': stores
    }

    return render(request, 'Reports.html', context)
