from django.test import TestCase
from django.test import Client
from hello.models import Person, RequestLog


class IndexTest(TestCase):

    fixtures = ['initial_data.json']

    def test_person_amount(self):
        """
        Tests whether there is no more than one person in the database"""

        self.assertLessEqual(len(Person.objects.all()), 1)

    def test_indexpage(self):
        """
        Tests whether GET to '/' returns response with 200 status code"""

        c = Client()
        response = c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['person'], Person.objects.all()[0])
        self.assertIn('Yevhen', response.content)
        self.assertIn('Yevsyuhov', response.content)
        self.assertIn('Sept. 16, 1997', response.content)
        self.assertIn('yevhen.yevsyuhov', response.content)
        self.assertIn('yevs@42cc.co', response.content)

    def test_indexpage_no_persons(self):
        """
        Tests whether GET to '/' receives right page"""

        c = Client()
        Person.objects.all()[0].delete()
        response = c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['person'])
        self.assertIn('No persons in the database', response.content)


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
        self.assertIn(
            '<tr>\n                        <td>'
            '28/01/2016 13:01</td>\n'
            '                        <td>GET</td>'
            '\n                        <td>/</td>'
            '\n                    </tr>', response.content)
