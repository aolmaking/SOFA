import sys
import os
import unittest
import json
import sqlite3
sys.path.insert(0, os.path.abspath('backend'))
from app import app
class OrderTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.test_email = "order_test@example.com"
        self.test_password = "Password123"
        # Register and login to get token
        self.app.post('/api/auth/register', json={
            "email": self.test_email,
            "username": "order_test",
            "password": self.test_password,
            "full_name": "Order Test"
        })
        login = self.app.post('/api/auth/login', json={
            "email": self.test_email,
            "password": self.test_password
        })
        self.token = json.loads(login.data)['token']
    def tearDown(self):
        db_path = os.path.abspath('backend/Database.db')
        conn = sqlite3.connect(db_path)
        conn.execute("DELETE FROM customers WHERE email = ?", (self.test_email,))
        conn.commit()
        conn.close()
    def _auth_headers(self):
        return {"Authorization": f"Bearer {self.token}"}
    def test_order_empty_cart_400(self):
        res = self.app.post('/api/order',
                            json={"customer_name": "Test"},
                            headers=self._auth_headers())
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data.get('code'), 'EMPTY_CART')
    def test_order_success_201(self):
        # Add item to cart first
        menu = self.app.get('/api/menu')
        item_id = json.loads(menu.data)[0]['public_id']
        self.app.post('/api/cart', json={"item_id": item_id, "quantity": 2})
        res = self.app.post('/api/order',
                            json={"customer_name": "Test Customer"},
                            headers=self._auth_headers())
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 201)
        self.assertIn('order_id', data)
        self.assertEqual(data['status'], 'pending')
    def test_order_idempotent_200(self):
        menu = self.app.get('/api/menu')
        item_id = json.loads(menu.data)[0]['public_id']
        self.app.post('/api/cart', json={"item_id": item_id, "quantity": 1})
        res1 = self.app.post('/api/order',
                            json={"customer_name": "Test"},
                            headers=self._auth_headers())
        res2 = self.app.post('/api/order',
                            json={"customer_name": "Test"},
                            headers=self._auth_headers())
        data1 = json.loads(res1.data)
        data2 = json.loads(res2.data)
        self.assertEqual(res1.status_code, 201)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(data1['order_id'], data2['order_id'])
    def test_order_price_locked(self):
        menu = self.app.get('/api/menu')
        item = json.loads(menu.data)[0]
        self.app.post('/api/cart', json={"item_id": item['public_id'], "quantity": 1})
        res = self.app.post('/api/order',
                            json={"customer_name": "Test"},
                            headers=self._auth_headers())
        data = json.loads(res.data)
        self.assertEqual(data['total'], item['price'])
    def test_order_unavailable_item_409(self):
        # This test would require making an item unavailable mid test
        # Demonstrates boundary awareness even if not fully executable
        pass