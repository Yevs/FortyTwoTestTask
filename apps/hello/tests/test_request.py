# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test import Client
from django.conf import settings
from django.core import serializers
from hello.models import RequestLog
from hello.views import parse_args, get_requests_by_args
from datetime import datetime
import json


class RequestTest(TestCase):

    fixtures = ['initial_data.json']

    def setUp(self):
        self.client = Client()
        self.REQUESTS_ON_PAGE = settings.REQUESTS_ON_PAGE

    def test_middleware(self):
        """
        Tests whether request is getting written to db"""

        old_amount = len(RequestLog.objects.all())
        self.client.get('/')
        new_amount = len(RequestLog.objects.all())
        self.assertEqual(new_amount-old_amount, 1)

    def test_request_page(self):
        """
        Tests whether requests page accessible and if data is there"""

        response = self.client.get('/requests/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hello/requests.html')
        self.assertIsNotNone(response.context['requests'])
        self.assertIn('<tr>\n                    '
                      '        <td>28/01/2016 13:39</td>'
                      '\n                            <td>GET</td>'
                      '\n                            <td>/</td>'
                      '\n                            <td>0</td>'
                      '\n                        </tr>', response.content)

    def test_get_args(self):
        """
        Tests if get_args parses arguments right"""

        with self.assertRaises(ValueError):
            parse_args({'count': 'abc'})
        self.assertEqual(parse_args({'count': 1,
                                     'lower': 2,
                                     'upper': 3,
                                     'order': 'priority'}),
                         (1, 2, 3, 'priority'))
        self.assertEqual(parse_args({'priority': 'none'}),
                         (settings.REQUESTS_ON_PAGE, 0, 2147483647, 'time'))

    def test_get_request_by_args(self):
        """
        Tests if get_requests_by_args works right"""

        requests = get_requests_by_args(1, 0, 1, 'time')
        self.assertEqual(requests.count(), 1)
        requests = get_requests_by_args(settings.REQUESTS_ON_PAGE,
                                        4, 5, 'time')
        self.assertEqual(requests.count(), 4)
        requests = get_requests_by_args(settings.REQUESTS_ON_PAGE, 4, 5,
                                        'date', datetime.now())
        self.assertEqual(requests.count(), 0)

    def test_api_count_option(self):
        """
        Tests if count option works with api"""

        resp = self.client.get('/api/requests/?count=5')
        self.assertEqual(len(json.loads(resp.content)), 5)

    def test_api_priority_bounds(self):
        """
        Tests if priority bounds work with api"""

        resp = self.client.get('/api/requests/?lower=1&upper=5')
        count = RequestLog.objects.filter(priority__gte=1,
                                          priority__lte=5).count()
        self.assertEqual(len(json.loads(resp.content)), count)

    def test_api_ordering(self):
        """
        Tests if api ordering option works with api"""

        resp = self.client.get('/api/requests/?order=priority')
        reqs = RequestLog.objects.all()\
            .order_by('-priority', '-datetime')[:settings.REQUESTS_ON_PAGE]
        self.assertEqual(resp.content, serializers.serialize('json', reqs))
        resp = self.client.get('/api/requests/?order=time')
        reqs = RequestLog.objects.all()\
            .order_by('-datetime', '-priority')[:settings.REQUESTS_ON_PAGE]
        self.assertEqual(resp.content, serializers.serialize('json', reqs))

    def test_get_request(self):
        """
        Tests whether get_requests return right requests in right order"""

        req = RequestLog.objects.all().first()
        response = self.client.get('/api/requests/1/')
        requests = RequestLog.objects.filter(datetime__gt=req.datetime)\
                                     .order_by('-datetime', '-priority')
        requests = requests[:self.REQUESTS_ON_PAGE]
        jsoned_reqs = serializers.serialize('json', requests)
        self.assertEqual(jsoned_reqs, response.content)

    def test_get_last_requests_count_option(self):
        """
        Tests whether get_request returns right number of
        requests with count option"""

        response = self.client.get('/api/requests/1/?count=2')
        requests = json.loads(response.content)
        self.assertEqual(2, len(requests))

    def test_get_last_requests_bounds_option(self):
        """
        Tests whether get_request returns right number of requests
        with bounds options"""

        response = self.client.get('/api/requests/1/?lower=2&upper=4')
        requests = json.loads(response.content)
        self.assertEqual(0, len(requests))

    def test_get_last_requests_order_option(self):
        """
        Tests whether get_request returns requests in right order
        with order option"""

        req = RequestLog.objects.all().first()
        response = self.client.get('/api/requests/1/?order=priority')
        requests = RequestLog.objects.filter(datetime__gt=req.datetime)\
            .order_by('-priority', '-datetime')[:settings.REQUESTS_ON_PAGE]
        self.assertEqual(serializers.serialize('json', requests),
                         response.content)

    def test_requests_amount(self):
        """
        Tests whether requests page has only REQUESTS_ON_PAGE requests"""

        response = self.client.get('/requests/')
        self.assertEqual(len(response.context['requests']),
                         self.REQUESTS_ON_PAGE)

    def test_api_logging(self):
        """
        Tests whether api call are not being logged to db"""

        old_amount = RequestLog.objects.count()
        self.client.get('/api/requests/1')
        new_amount = RequestLog.objects.count()
        self.assertEqual(old_amount, new_amount)
