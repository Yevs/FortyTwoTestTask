# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test import Client
from hello.models import Person, RequestLog
from datetime import datetime
import json


class PersonTest(TestCase):

    fixtures = ['initial_data.json']

    def test_unicode(self):
        """
        Tests assigning unicode values to Person model's fields"""
        p = Person.objects.first()
        name = u'Аркадий'
        p.first_name = name
        p.save()
        self.assertEqual(Person.objects.first().first_name, name)
        c = Client()
        response = c.get('/')
        self.assertIn(name, response.content.decode('utf-8'))


class IndexTest(TestCase):

    fixtures = ['initial_data.json']

    def setUp(self):
        self.client = Client()

    def test_indexpage(self):
        """
        Tests whether GET to '/' returns response with 200 status code"""

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['person'],
                         Person.objects.order_by('id').first())
        content = response.content.decode('utf-8')
        self.assertIn('Yevhen', content)
        self.assertIn('Yevsyuhov', content)
        self.assertIn('Sept. 16, 1997', content)
        self.assertIn('yevhen.yevsyuhov', content)
        self.assertIn('yevs@42cc.co', content)

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


class RequestTest(TestCase):

    fixtures = ['request_fixtures.json']

    def test_middleware(self):
        """
        Tests whether request is getting written to db"""

        old_amount = len(RequestLog.objects.all())
        Client().get('/')
        new_amount = len(RequestLog.objects.all())
        self.assertEqual(new_amount-old_amount, 1)

    def test_request_page(self):
        """
        Tests whether requests page accessible and if data is there"""

        c = Client()
        response = c.get('/requests/')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['requests'])
        self.assertIn('<tr>\n'
                      '                            <td>28/01/2016 13:01</td>\n'
                      '                            <td>GET</td>\n'
                      '                            <td>/</td>\n'
                      '                        </tr>', response.content)

    def test_get_request(self):
        """
        Tests whethe get_requests return right requests in right order"""

        c = Client()
        req = RequestLog.objects.all().first()
        response = c.get('/api/requests/1/')
        requests = RequestLog.objects.filter(datetime__gt=req.datetime)
        requests = requests.exclude(path__contains='/api/')
        jsoned_reqs = json.dumps([{
                          'datetime': r.datetime.strftime('%d/%m/%Y %H:%M'),
                          'method': str(r.method),
                          'path': str(r.path),
                          'id': str(r.id)} for r in requests])
        self.assertEqual(jsoned_reqs, response.content)
