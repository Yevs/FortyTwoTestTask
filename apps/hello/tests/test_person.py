# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test import Client
from hello.models import Person
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

    def test_to_dict(self):
        """
        Tests if to_dict method returns right value"""

        p = Person.objects.first()
        self.assertEqual(json.dumps(p.get_dict()),
                         '{"first_name": "Yevhen",'
                         ' "last_name":'
                         ' "Yevsyuhov", "other_contacts":'
                         ' "phone: 0971339340",'
                         ' "email": "yevhen.yevsyuhov@gmail.com",'
                         ' "avatar": "/uploads/avatars/default.png",'
                         ' "skype": "yevhen.yevsyuhov",'
                         ' "birth_date": "1997-09-16",'
                         ' "jabber": "yevs@42cc.co",'
                         ' "id": 1,'
                         ' "biography": "I was born'
                         ' 16th of September in 1997.'
                         '  During my childhood I liked'
                         ' to play videogames a lot.'
                         '  That\'s what made me curious'
                         ' about computers and how '
                         'they work. Now I am receiving'
                         ' CS Bachelor degree at NTUU \'KPI\'"}')
