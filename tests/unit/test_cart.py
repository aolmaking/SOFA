import sys
import os
import unittest
import json
sys.path.insert(0, os.path.abspath('backend'))
from app import app
class CartTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    def _get_session_cookie(self, response):
        return response.headers.getlist('Set-Cookie')
    def test_cart_add_item(self):
        # Get a menu item
        menu = self.app.get('/api/menu')
        items = json.loads(menu.data)
        item_id = items[0]['public_id']
        res = self.app.post('/api/cart', json={
            "item_id": item_id,
            "quantity": 2
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(data.get('message'), 'Item added to cart')
    def test_cart_reject_unavailable(self):
        # This test assumes at least one unavailable item exists in seed data
        res = self.app.post('/api/cart', json={
            "item_id": "non-existent-id",
            "quantity": 1
        })
        self.assertEqual(res.status_code, 404)
    def test_cart_reject_out_of_range(self):
        menu = self.app.get('/api/menu')
        items = json.loads(menu.data)
        item_id = items[0]['public_id']
        res = self.app.post('/api/cart', json={
            "item_id": item_id,
            "quantity": 25
        })
        self.assertEqual(res.status_code, 400)
    def test_cart_update_quantity(self):
        menu = self.app.get('/api/menu')
        items = json.loads(menu.data)
        item_id = items[0]['public_id']
        self.app.post('/api/cart', json={"item_id": item_id, "quantity": 1})
        res = self.app.patch(f'/api/cart/{item_id}', json={"quantity": 3})
        self.assertEqual(res.status_code, 200)
    def test_cart_remove_item(self):
        menu = self.app.get('/api/menu')
        items = json.loads(menu.data)
        item_id = items[0]['public_id']
        self.app.post('/api/cart', json={"item_id": item_id, "quantity": 1})
        res = self.app.delete(f'/api/cart/{item_id}')
        self.assertEqual(res.status_code, 200)