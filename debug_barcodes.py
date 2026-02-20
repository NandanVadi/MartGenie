from products.models import Product
products = Product.objects.all()
print(f"Total products: {len(products)}")
for p in products:
    print(f"Barcode: {repr(p.barcode)} Len: {len(p.barcode)}")
