import sys
import os
import unittest
import json
sys.path.insert(0, os.path.abspath('backend'))
from app import app
class MenuTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    def test_menu_list_all(self):
        res = self.app.get('/api/menu')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    def test_menu_filter_category(self):
        res = self.app.get('/api/menu?category=coffee')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        for item in data:
            self.assertEqual(item['category'], 'coffee')
    def test_menu_hides_unavailable(self):
        res = self.app.get('/api/menu')
        data = json.loads(res.data)
        available_items = [i for i in data if i.get('available')]
        self.assertEqual(len(available_items), len(data))
    def test_menu_exposes_public_id_only(self):
        res = self.app.get('/api/menu')
        data = json.loads(res.data)
        for item in data:
            self.assertIn('public_id', item)
            self.assertNotIn('id', item)