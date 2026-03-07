from billing.models import Order, GatePassLog
print("=== Orders with QR Data ===")
for o in Order.objects.filter(user__role='CUSTOMER').order_by('-created_at'):
    qr = (o.qr_data or '')[:60]
    print(f"Order: {o.order_id} | QR Data: '{qr}'")

print("\n=== Gate Pass Logs ===")
for g in GatePassLog.objects.all().order_by('-verified_at'):
    print(f"Pass: {g.order.order_id} | Status: {g.status} | Time: {g.verified_at}")
