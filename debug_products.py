from products.models import Product
from core.models import Store

print("Starting debug...")
try:
    store = Store.objects.first()
    print(f"Store: {store}")
except Exception as e:
    print(f"Store Error: {e}")

products = Product.objects.all()
print(f"Total products: {len(products)}")

for p in products:
    print(f"Checking {p.name} ({p.barcode})")
    try:
        price = float(p.price)
    except Exception as e:
        print(f"  Price Error: {e}")
        
    try:
        if p.image:
            # Accessing url might trigger storage check or db issue
            url = p.image.url
            print(f"  Image URL: {url}")
        else:
            print("  No Image")
    except Exception as e:
        print(f"  Image Error: {e}")
