from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser
from core.models import Store
from products.models import Product
from billing.models import Order
from inventory.models import InventoryItem
import json

class SecureCheckoutTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create user
        self.user = CustomUser.objects.create_user(username='test_cust', password='password123', role='CUSTOMER')
        self.admin = CustomUser.objects.create_user(username='test_admin', password='password123', role='ADMIN')
        
        # Create store
        self.store = Store.objects.create(name='Test Store', store_code='TEST_STORE_123', admin=self.admin)
        
        # Create product (Real Price: 500)
        self.product = Product.objects.create(name='Test Item', barcode='12345', price=500.00)
        
        # Create corresponding inventory item (Stock: 2)
        self.inventory = InventoryItem.objects.create(store=self.store, product=self.product, quantity=2, low_stock_threshold=5)
        
        # Login
        self.client.login(username='test_cust', password='password123')
        
        # Set session
        session = self.client.session
        session['store_code'] = 'TEST_STORE_123'
        session.save()

    def test_price_trust_validation(self):
        """
        Tests that if the frontend attempts to pass a fake 'total' (e.g. 10.00 instead of 500.00),
        the backend ignores it and charges the real price.
        """
        fake_payload = {
            'orderId': 'ORD-FAKEPRICE',
            'total': 10.00,  # Hacker tries to pay 10 rupees for a 500 product
            'qrData': 'QR123',
            'items': [
                {'id': '12345', 'name': 'Test Item', 'quantity': 1, 'price': 10.00} # Fake price
            ]
        }
        response = self.client.post(reverse('create_order'), data=json.dumps(fake_payload), content_type='application/json')
        
        self.assertEqual(response.status_code, 200) # Order completes
        order = Order.objects.get(order_id='ORD-FAKEPRICE')
        
        # KEY ASSERT: The total must be 500.00, ignoring the hacker's 10.00
        self.assertEqual(order.total_amount, 500.00) 

    def test_insufficient_inventory_block(self):
        """
        Tests that requesting more stock than available triggers a strict 400 Bad Request error.
        """
        payload = {
            'orderId': 'ORD-NOSTOCK',
            'total': 5000.00,
            'qrData': 'QR123',
            'items': [
                {'id': '12345', 'name': 'Test Item', 'quantity': 10, 'price': 500.00} # Asking for 10, only 2 in DB
            ]
        }
        response = self.client.post(reverse('create_order'), data=json.dumps(payload), content_type='application/json')
        
        # KEY ASSERT: Must fail.
        self.assertEqual(response.status_code, 400)
        self.assertIn("Insufficient stock", response.json().get('message'))
        
        # DB ASSERT: Inventory must not have gone negative
        inventory = InventoryItem.objects.get(id=self.inventory.id)
        self.assertEqual(inventory.quantity, 2)

    def test_session_fallback_security(self):
        """
        Tests that missing store_code in session forces checkout to fail instead of fallback.
        """
        # Clear session
        session = self.client.session
        del session['store_code']
        session.save()
        
        payload = {
            'orderId': 'ORD-NOSESSION',
            'total': 500.00,
            'qrData': 'QR123',
            'items': [
                {'id': '12345', 'name': 'Test Item', 'quantity': 1, 'price': 500.00}
            ]
        }
        
        response = self.client.post(reverse('create_order'), data=json.dumps(payload), content_type='application/json')
        
        # KEY ASSERT: Must fail. No session = no store fallback routing.
        self.assertEqual(response.status_code, 400)
        self.assertIn("Store session lost", response.json().get('message'))
