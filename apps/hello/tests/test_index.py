# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test import Client
from hello.models import Person
from datetime import datetime


class IndexTest(TestCase):

    fixtures = ['initial_data.json']

    def setUp(self):
        self.client = Client()
        self.auth_client = Client()
        self.auth_client.login(username='user',
                               password='user')

    def test_indexpage(self):
        """
        Tests whether GET to '/' returns response with 200 status code"""

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hello/index.html')
        self.assertEqual(response.context['person'], Person.objects.all()[0])
        self.assertIn('Yevhen', response.content)
        self.assertIn('Yevsyuhov', response.content)
        self.assertIn('1997-09-16', response.content)
        self.assertIn('yevhen.yevsyuhov', response.content)
        self.assertIn('yevs@42cc.co', response.content)

    def test_index_no_auth_button(self):
        """
        Tests whether user cannot edit data if not logged in"""

        response = self.client.get('/')
        self.assertNotIn('<button id="edit" class="btn btn-primary"'
                         '>Edit</button>', response.content)

    def test_index_auth_button(self):
        """
        Tests whether user can edit data if logged in"""

        response = self.auth_client.get('/')
        self.assertIn('<button id="edit" class="btn btn-primary"'
                      '>Edit</button>', response.content)

    def test_indexpage_no_persons(self):
        """
        Tests whether GET to '/' receives right page"""

        Person.objects.first().delete()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['person'])
        self.assertIn('No persons in the database', response.content)

    def test_indexpage_multiple_persons(self):
        """
        Tests whether GET to '/' receives page only
        with first person(smallest id) from the db"""

        Person(first_name='Sasha', last_name='Bilyy',
               email='a@a.com', birth_date=datetime.now()).save()
        response = self.client.get('/')
        self.assertIn('Yevhen', response.content.decode('utf-8'))
