from django.test import TestCase
from django.test import Client

# Create your tests here.

class IndexTest(TestCase):

    def test_indexpage(self):
        """
        Tests whether GET to '/' returns response with 200 status code"""
        
        c = Client()
        response = c.get('/')
        self.assertEqual(response.status_code, 200)
