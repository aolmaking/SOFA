import sys
import os
import unittest
import json
import sqlite3

sys.path.insert(0, os.path.abspath('backend'))
from app import app

class IntegrationIsolationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # User A
        self.app.post('/api/auth/register', json={
            "email": "user_a@example.com",
            "username": "user_a",
            "password": "Password123",
            "full_name": "User A"
        })
        login_a = self.app.post('/api/auth/login', json={
            "email": "user_a@example.com",
            "password": "Password123"
        })
        self.token_a = json.loads(login_a.data)['token']
        
        # User B
        self.app.post('/api/auth/register', json={
            "email": "user_b@example.com",
            "username": "user_b",
            "password": "Password123",
            "full_name": "User B"
        })
        login_b = self.app.post('/api/auth/login', json={
            "email": "user_b@example.com",
            "password": "Password123"
        })
        self.token_b = json.loads(login_b.data)['token']

    def tearDown(self):
        db_path = os.path.abspath('backend/Database.db')
        conn = sqlite3.connect(db_path)
        for email in ["user_a@example.com", "user_b@example.com"]:
            conn.execute("DELETE FROM customers WHERE email = ?", (email,))
        conn.commit()
        conn.close()

    def test_history_isolation_user_a_b(self):
        # User A places an order
        menu = self.app.get('/api/menu')
        item_id = json.loads(menu.data)[0]['public_id']
        self.app.post('/api/cart', json={"item_id": item_id, "quantity": 1})
        self.app.post('/api/order',
                            json={"customer_name": "User A"},
                            headers={"Authorization": f"Bearer {self.token_a}"})
        
        # User B checks history---should not see User A’s order
        res = self.app.get('/api/history',
                            headers={"Authorization": f"Bearer {self.token_b}"})
        data = json.loads(res.data)
        self.assertEqual(len(data.get('orders', [])), 0)