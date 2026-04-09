from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product
from inventory.models import InventoryItem
from core.models import Store
import urllib.request
import json as _json


@login_required
@require_GET
def barcode_lookup(request, barcode):
    """
    Server-side proxy for barcode lookup.
    Tries multiple APIs in order:
      1. Open Food Facts India  (best for Indian products)
      2. Open Food Facts World  (global fallback)
      3. UPCitemdb              (100 free/day, good for branded goods)
    Returns: { found: true, name, category, image, source } or { found: false }
    """
    barcode = barcode.strip()

    def _fetch(url, timeout=5):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'MartGenie/1.0'})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return _json.loads(resp.read().decode())
        except Exception:
            return None

    # 1. Open Food Facts India
    d = _fetch(f'https://in.openfoodfacts.org/api/v0/product/{barcode}.json')
    if d and d.get('status') == 1 and d.get('product', {}).get('product_name'):
        p = d['product']
        cats = p.get('categories', '')
        return JsonResponse({
            'found': True,
            'name': p['product_name'],
            'category': cats.split(',')[0].strip() if cats else '',
            'image': p.get('image_url', ''),
            'source': 'Open Food Facts India',
        })

    # 2. Open Food Facts World
    d = _fetch(f'https://world.openfoodfacts.org/api/v0/product/{barcode}.json')
    if d and d.get('status') == 1 and d.get('product', {}).get('product_name'):
        p = d['product']
        cats = p.get('categories', '')
        return JsonResponse({
            'found': True,
            'name': p['product_name'],
            'category': cats.split(',')[0].strip() if cats else '',
            'image': p.get('image_url', ''),
            'source': 'Open Food Facts',
        })

    # 3. UPCitemdb (100 free/day)
    d = _fetch(f'https://api.upcitemdb.com/prod/trial/lookup?upc={barcode}')
    if d and d.get('code') == 'OK' and d.get('items'):
        item = d['items'][0]
        images = item.get('images', [])
        return JsonResponse({
            'found': True,
            'name': item.get('title', ''),
            'category': item.get('category', ''),
            'image': images[0] if images else '',
            'source': 'UPCitemdb',
        })

    return JsonResponse({'found': False})

@login_required
@require_GET
def get_products(request, store_code):
    try:
        # Normalized store code matching
        store_code = (store_code or '').strip()
        store = Store.objects.filter(store_code=store_code).first()
        
        if not store:
             return JsonResponse([], safe=False)

        # Optional search query
        search_query = request.GET.get('q', '').strip()

        # Get products (filtered if search query exists)
        if search_query:
            all_products = Product.objects.filter(
                Q(name__icontains=search_query) |
                Q(barcode__icontains=search_query) |
                Q(category__icontains=search_query),
                inventory_items__store=store
            ).distinct()
        else:
            all_products = Product.objects.filter(inventory_items__store=store).distinct()
        
        limit = request.GET.get('limit', '').strip().lower()

        if limit == 'all':
            # Bypass pagination for scanner
            page_obj = all_products
            paginated = False
        else:
            # Pagination (10 products per page)
            page_number = request.GET.get('page', 1)
            paginator = Paginator(all_products, 10)
            page_obj = paginator.get_page(page_number)
            paginated = True
        
        # Get inventory mapping
        inventory_map = {
            item.product_id: item.quantity 
            for item in InventoryItem.objects.filter(store=store)
        }
        
        products_data = []
        for product in page_obj:
            qty = inventory_map.get(product.id, 0)
            products_data.append({
                'id': product.barcode, 
                'name': product.name,
                'price': float(product.price),
                'category': product.category,
                'barcode': product.barcode,
                'quantity_available': qty,
                'image_url': product.image.url if product.image else ''
            })
            
        if not paginated:
             return JsonResponse({'products': products_data})

        return JsonResponse({
            'products': products_data,

            'page': page_obj.number,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        })

    except Exception as e:
        return JsonResponse([], safe=False)


from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
import json

@staff_member_required
def inventory_manager(request):
    return render(request, 'products/inventory_manager.html')


@csrf_exempt
@staff_member_required
def inventory_api(request):

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            barcode = data.get('barcode', '').strip()
            
            if not barcode:
                return JsonResponse({'status': 'error', 'message': 'Barcode required'})

            # Find product
            product = Product.objects.filter(barcode=barcode).first()
            
            # Find store belonging to this admin
            selected_store_id = request.session.get('admin_selected_store')
            if selected_store_id and selected_store_id != 'all':
                store = Store.objects.filter(admin=request.user, id=selected_store_id).first()
            else:
                store = Store.objects.filter(admin=request.user).first()

            if not store:
                 return JsonResponse({'status': 'error', 'message': 'No store selected or configured'})
            
            if action == 'fetch':

                if product:

                    inv_item, _ = InventoryItem.objects.get_or_create(store=store, product=product)

                    return JsonResponse({
                        'status': 'found',
                        'product': {
                            'name': product.name,
                            'price': float(product.price),
                            'current_stock': inv_item.quantity,
                            'image': product.image.url if product.image else ''
                        }
                    })
                else:
                    return JsonResponse({'status': 'not_found', 'barcode': barcode})
            
            elif action == 'update_stock':

                qty_change = int(data.get('quantity', 0))

                if product:
                    inv_item, _ = InventoryItem.objects.get_or_create(store=store, product=product)

                    inv_item.quantity = max(0, inv_item.quantity + qty_change)

                    inv_item.save()

                    return JsonResponse({'status': 'success', 'new_stock': inv_item.quantity})
            
            elif action == 'create_product':

                name = data.get('name')
                price = data.get('price')
                category = data.get('category')
                
                product = Product.objects.create(
                    name=name,
                    barcode=barcode,
                    price=price,
                    category=category
                )

                # Initialize inventory
                InventoryItem.objects.create(
                    store=store,
                    product=product,
                    quantity=data.get('initial_stock', 0)
                )
                
                return JsonResponse({'status': 'success', 'message': 'Product created'})

        except Exception as e:

            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid method'})
