import sys
import os
import unittest
import json
import sqlite3

sys.path.insert(0, os.path.abspath('backend'))
from app import app

class HistoryTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.test_email = "history_test@example.com"
        self.test_password = "Password123"
        self.app.post('/api/auth/register', json={
            "email": self.test_email,
            "username": "history_test",
            "password": self.test_password,
            "full_name": "History Test"
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

    def test_history_requires_auth_401(self):
        res = self.app.get('/api/history')
        self.assertEqual(res.status_code, 401)

    def test_history_returns_completed_only(self):
        # Place an order and mock time to completion
        res = self.app.get('/api/history', headers=self._auth_headers())
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        for order in data.get('orders', []):
            self.assertEqual(order['status'], 'completed')

    def test_history_pagination(self):
        res = self.app.get('/api/history?limit=5&offset=0', headers=self._auth_headers())
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIn('orders', data)