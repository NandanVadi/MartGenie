from products.models import Product
with open('debug_output.txt', 'w') as f:
    products = Product.objects.all()
    f.write(f"Total products: {len(products)}\n")
    for p in products:
        f.write(f"Barcode: {repr(p.barcode)} Len: {len(p.barcode)}\n")
