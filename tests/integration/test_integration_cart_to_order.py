import sys
import os
import unittest
import json
import sqlite3

sys.path.insert(0, os.path.abspath('backend'))
from app import app

class IntegrationCartOrderTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.test_email = "int_cart@example.com"
        self.test_password = "Password123"
        self.app.post('/api/auth/register', json={
            "email": self.test_email,
            "username": "int_cart",
            "password": self.test_password,
            "full_name": "Integration Cart"
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

    def test_add_to_cart_then_order(self):
        # Get menu item
        menu = self.app.get('/api/menu')
        item_id = json.loads(menu.data)[0]['public_id']
        
        # Add to cart
        res1 = self.app.post('/api/cart', json={
            "item_id": item_id,
            "quantity": 2
        })
        self.assertEqual(res1.status_code, 201)
        
        # Place order
        res2 = self.app.post('/api/order',
                            json={"customer_name": "Integration Test"},
                            headers=self._auth_headers())
        data2 = json.loads(res2.data)
        self.assertEqual(res2.status_code, 201)
        
        # Verify cart is empty
        res3 = self.app.get('/api/cart')
        data3 = json.loads(res3.data)
        self.assertEqual(len(data3.get('items', [])), 0)

    def test_order_then_track_progression(self):
        menu = self.app.get('/api/menu')
        item_id = json.loads(menu.data)[0]['public_id']
        self.app.post('/api/cart', json={"item_id": item_id, "quantity": 1})
        
        res = self.app.post('/api/order',
                            json={"customer_name": "Track Test"},
                            headers=self._auth_headers())
        order_id = json.loads(res.data)['order_id']
        
        # Track active
        res2 = self.app.get('/api/track/active', headers=self._auth_headers())
        data2 = json.loads(res2.data)
        active = [o for o in data2['orders'] if o['order_id'] == order_id]
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0]['status'], 'pending')