# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from hello.models import Person, ModelChange
from datetime import datetime


class SignalTest(TestCase):

    fixtures = ['initial_data.json']

    def test_add(self):
        """
        Tests if adding a Person would create and 'add' db entry"""

        p = Person(first_name='John',
                   last_name='Doe',
                   email='john@doe.com',
                   birth_date=datetime.now())
        p.save()
        logs = ModelChange.objects.filter(instance_pk=p.pk)
        self.assertTrue(logs.exists())
        self.assertEqual(logs.first().type, 'add')

    def test_edit(self):
        """
        Tests if changing a Person would create an 'edit' db entry"""

        p = Person.objects.first()
        p.first_name = 'John'
        p.save()
        logs = ModelChange.objects.filter(model='Person',
                                          instance_pk=p.pk)
        self.assertTrue(logs.exists())
        self.assertEqual(logs.last().type, 'edit')

    def test_delete(self):
        """
        Tests if deleting a Person would create a 'delete' db entry"""

        p = Person.objects.first()
        pk = p.pk
        p.delete()
        logs = ModelChange.objects.filter(model='Person',
                                          instance_pk=pk)
        self.assertTrue(logs.exists())
        self.assertEqual(logs.last().type, 'delete')

    def test_ignore_add(self):
        """
        Tests if adding a model from ignore list would not create db entry"""

        old_count = ModelChange.objects.count()
        ContentType(app_label='hello', model='abc').save()
        new_count = ModelChange.objects.count()
        self.assertEqual(new_count, old_count)

    def test_ignore_edit(self):
        """
        Tests if changing instance of a model from ignore list
        would not create db entry"""

        c = ContentType(app_label='hello', model='abc')
        c.save()
        old_count = ModelChange.objects.count()
        c.model = 'cba'
        c.save()
        new_count = ModelChange.objects.count()
        self.assertEqual(old_count, new_count)

    def test_ignore_delete(self):
        """
        Tests if deleting instance of a model from ignore list
        would not create db entry"""

        c = ContentType(app_label='hello', model='abc')
        c.save()
        old_count = ModelChange.objects.count()
        c.delete()
        new_count = ModelChange.objects.count()
        self.assertEqual(old_count, new_count)
