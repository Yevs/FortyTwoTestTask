# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test import Client
from hello.models import Person
from PIL import Image
import os
import json


class EditTest(TestCase):

    fixtures = ['initial_data.json']

    def setUp(self):
        self.client = Client()
        self.auth_client = Client()
        self.auth_client.login(username='user', password='user')

    def test_api_no_auth(self):
        """
        Tests if it is not possible to change model instance
        via api if you are not logged in"""

        data = {'first_name': 'William',
                'last_name': 'Doe',
                'biography': '',
                'email': 'w@doe.com',
                'skype': '',
                'jabber': '',
                'other_contacts': '',
                'birth_date': '1999-01-01'}

        resp = self.client.post('/api/edit/', data)
        self.assertEqual(resp.status_code, 302)

    def test_api(self):
        """
        Tests if api function works"""

        data = {'first_name': 'William',
                'last_name': 'Doe',
                'biography': '',
                'email': 'w@doe.com',
                'skype': '',
                'jabber': '',
                'other_contacts': '',
                'birth_date': '1999-01-01'}

        with open('uploads/avatars/default.png') as img:

            data['avatar'] = img
            resp = self.auth_client.post('/api/edit/', data)
            result = json.loads(resp.content)
            self.assertEqual(result['status'], 'ok')
            p = Person.objects.first()
            self.assertEqual(p.first_name, u'William')
            self.assertNotEqual(p.avatar, 'avatars/default.png')
            os.remove('uploads/' + str(p.avatar))

    def test_form_validation(self):
        """
        Tests form validation(but not image)"""

        data = {'first_name': '',
                'last_name': '',
                'email': '',
                'birth_date': ''}

        resp = self.auth_client.post('/api/edit/', data)
        self.assertEqual('{"status": "error", "errors":'
                         ' {"birth_date": ["This field is required."],'
                         ' "first_name": ["This field is required."],'
                         ' "last_name": ["This field is required."],'
                         ' "email": ["This field is required."]}}',
                         resp.content)

    def test_image_validation(self):
        """
        Tests if submitting wrong file type validates"""

        with open('assets/css/hello/style.css') as img:
            data = {'avatar': img}
            resp = self.auth_client.post('/api/edit/', data)
            result = json.loads(resp.content)
            self.assertEqual(result['status'], 'error')
            self.assertEqual('Upload a valid image. The file you uploaded was'
                             ' either not an image or a corrupted image.',
                             result['errors']['avatar'][0])

    def test_image_resize(self):

        """
        Tests if submited image gets resized"""

        theFile = 'uploads/avatars/default.png'

        img = Image.open(theFile)
        resized = img.resize((300, 300))
        resized.save('tmp.png')

        data = {'first_name': 'William',
                'last_name': 'Doe',
                'biography': '',
                'email': 'w@doe.com',
                'skype': '',
                'jabber': '',
                'other_contacts': '',
                'birth_date': '1999-01-01'}

        with open('tmp.png') as img:
            data['avatar'] = img
            resp = self.auth_client.post('/api/edit/', data)
            result = json.loads(resp.content)
            self.assertEqual(result['status'], 'ok')
            self.assertEqual(200, Person.objects.first().avatar.height)
            self.assertEqual(200, Person.objects.first().avatar.width)

        os.remove('tmp.png')
