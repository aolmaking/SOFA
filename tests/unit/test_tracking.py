import sys
import os
import unittest
import json
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import patch

sys.path.insert(0, os.path.abspath('backend'))
from app import app

class TrackingTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.test_email = "track_test@example.com"
        self.test_password = "Password123"
        self.app.post('/api/auth/register', json={
            "email": self.test_email,
            "username": "track_test",
            "password": self.test_password,
            "full_name": "Track Test"
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

    def _place_order(self):
        menu = self.app.get('/api/menu')
        item_id = json.loads(menu.data)[0]['public_id']
        self.app.post('/api/cart', json={"item_id": item_id, "quantity": 1})
        res = self.app.post('/api/order',
                            json={"customer_name": "Test"},
                            headers=self._auth_headers())
        return json.loads(res.data)['order_id']

    def test_tracking_initial_pending(self):
        order_id = self._place_order()
        res = self.app.get('/api/track/active', headers=self._auth_headers())
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        order = [o for o in data['orders'] if o['order_id'] == order_id][0]
        self.assertEqual(order['status'], 'pending')

    @patch('backend.tracking.routes.datetime')
    def test_tracking_preparing_after_3min(self, mock_dt):
        order_id = self._place_order()
        # Mock time to 3 minutes in the future
        future = datetime.utcnow() + timedelta(minutes=3)
        mock_dt.utcnow.return_value = future
        res = self.app.get('/api/track/active', headers=self._auth_headers())
        data = json.loads(res.data)
        order = [o for o in data['orders'] if o['order_id'] == order_id][0]
        self.assertEqual(order['status'], 'preparing')

    @patch('backend.tracking.routes.datetime')
    def test_tracking_ready_after_5min(self, mock_dt):
        order_id = self._place_order()
        future = datetime.utcnow() + timedelta(minutes=5)
        mock_dt.utcnow.return_value = future
        res = self.app.get('/api/track/active', headers=self._auth_headers())
        data = json.loads(res.data)
        order = [o for o in data['orders'] if o['order_id'] == order_id][0]
        self.assertEqual(order['status'], 'ready')

    @patch('backend.tracking.routes.datetime')
    def test_tracking_completed_after_7min(self, mock_dt):
        order_id = self._place_order()
        future = datetime.utcnow() + timedelta(minutes=7)
        mock_dt.utcnow.return_value = future
        res = self.app.get('/api/track/history', headers=self._auth_headers())
        data = json.loads(res.data)
        order = [o for o in data['orders'] if o['order_id'] == order_id][0]
        self.assertEqual(order['status'], 'completed')
        self.assertEqual(len(order['timeline']), 4)