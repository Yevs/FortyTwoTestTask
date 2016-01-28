from django.test import TestCase
from django.test import Client
from hello.models import Person


class IndexTest(TestCase):

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

    def test_indexpage_no_persons(self):
        """
        Tests whether GET to '/' receives right page"""

        c = Client()
        Person.objects.all()[0].delete()
        response = c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['person'])
