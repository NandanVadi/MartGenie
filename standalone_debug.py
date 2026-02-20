import os
import django
import sys

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "martgenie.settings")
django.setup()

from products.models import Product

with open('debug_output_standalone.txt', 'w') as f:
    products = Product.objects.all()
    f.write(f"Total products: {len(products)}\n")
    for p in products:
        f.write(f"Barcode: {repr(p.barcode)} Len: {len(p.barcode)}\n")
