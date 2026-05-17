import sys
import os
import unittest
import json
import sqlite3

sys.path.insert(0, os.path.abspath('backend'))
from app import app

class IntegrationAuthFlowTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.test_email = "int_auth@example.com"
        self.test_password = "Password123"

    def tearDown(self):
        db_path = os.path.abspath('backend/Database.db')
        conn = sqlite3.connect(db_path)
        conn.execute("DELETE FROM customers WHERE email = ?", (self.test_email,))
        conn.commit()
        conn.close()

    def test_register_then_login_flow(self):
        # Register
        res1 = self.app.post('/api/auth/register', json={
            "email": self.test_email,
            "username": "int_auth",
            "password": self.test_password,
            "full_name": "Integration Auth"
        })
        self.assertEqual(res1.status_code, 201)

        # Login
        res2 = self.app.post('/api/auth/login', json={
            "email": self.test_email,
            "password": self.test_password
        })
        data2 = json.loads(res2.data)
        self.assertEqual(res2.status_code, 200)
        self.assertIn('token', data2)

        # Use token on /api/auth/me
        res3 = self.app.get('/api/auth/me', headers={
            "Authorization": f"Bearer {data2['token']}"
        })
        data3 = json.loads(res3.data)
        self.assertEqual(res3.status_code, 200)
        self.assertEqual(data3['email'], self.test_email)