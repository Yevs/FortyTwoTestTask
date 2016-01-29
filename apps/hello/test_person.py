from django.test import TestCase
from django.core.exceptions import ValidationError
from hello.models import Person
from datetime import datetime


class PersonTest(TestCase):

    fixtures = ['initial_data.json']

    def test_person_amount(self):
        """
        Tests whether there is no more than one person in the database"""

        self.assertLessEqual(len(Person.objects.all()), 1)

    def test_adding_more_than_one_person(self):
        """
        Test wheter it is forbidden to add more than one person to db"""

        p = Person(first_name='a', last_name='a', birth_date=datetime.now())
        with self.assertRaises(ValidationError):
            p.save()

    def test_adding(self):
        """
        Tests if you can add person to db if there is none"""

        Person.objects.first().delete()
        p = Person(first_name='a', last_name='a', birth_date=datetime.now())
        p.save()
