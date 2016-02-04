# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test import Client
from hello.models import Person, RequestLog
from datetime import datetime
from PIL import Image
import json
import os


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
        self.assertTemplateUsed(response, 'hello/index.html')
        self.assertEqual(response.context['person'], Person.objects.all()[0])
        self.assertIn('Yevhen', response.content)
        self.assertIn('Yevsyuhov', response.content)
        self.assertIn('Sept. 16, 1997', response.content)
        self.assertIn('yevhen.yevsyuhov', response.content)
        self.assertIn('yevs@42cc.co', response.content)

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

    def setUp(self):
        self.client = Client()
        self.REQUESTS_ON_PAGE = 10

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
        self.assertIn('<tr>\n'
                      '                            <td>28/01/2016 13:01</td>\n'
                      '                            <td>GET</td>\n'
                      '                            <td>/</td>\n'
                      '                        </tr>', response.content)

    def test_get_request(self):
        """
        Tests whether get_requests return right requests in right order"""

        req = RequestLog.objects.all().first()
        response = self.client.get('/api/requests/1/')
        requests = RequestLog.objects.filter(datetime__gt=req.datetime)\
                                     .order_by('-datetime')
        requests = requests[:self.REQUESTS_ON_PAGE]
        jsoned_reqs = json.dumps([{
                          'datetime': r.datetime.strftime('%d/%m/%Y %H:%M'),
                          'method': str(r.method),
                          'path': str(r.path),
                          'id': str(r.id)} for r in requests])
        self.assertEqual(jsoned_reqs, response.content)

    def test_requests_amount(self):
        """
        Tests whether requests page has only REQUESTS_ON_PAGE requests"""

        response = self.client.get('/requests/')
        self.assertEqual(len(response.context['requests']),
                         self.REQUESTS_ON_PAGE)

    def test_api_logging(self):
        """
        Tests whether api call are not being logged"""

        old_amount = RequestLog.objects.count()
        self.client.get('/api/requests/1')
        new_amount = RequestLog.objects.count()
        self.assertEqual(old_amount, new_amount)


class EditTest(TestCase):

    fixtures = ['initial_data.json']

    def setUp(self):
        self.client = Client()
        self.auth_client = Client()
        self.auth_client.login(username='user', password='user')

    def test_edit_page_no_auth(self):
        """
        Tests whether GET to /edit/ responds with HTTP 302
        if user is not authenticated"""

        response = self.client.get('/edit/')
        self.assertEqual(response.status_code, 302)

    def test_edit_template(self):
        """
        Tests whether GET to /edit/ responds with right template"""

        response = self.auth_client.get('/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hello/form.html')

    def test_form_on_edit_page(self):
        """
        Tests wheter there is form on /edit/ page"""

        response = self.auth_client.get('/edit/')
        self.assertIn('<form action="/edit" method="post"'
                      ' class="form-horizontal"'
                      ' enctype="multipart/form-data" id="edit-form">',
                      response.content)

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
