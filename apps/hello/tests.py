# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test import Client
from django.core import serializers
from django.core.management import call_command
from django.template import Context, Template
from django.utils.six import StringIO

from mock import patch
from PIL import Image
from datetime import datetime
import json
import os

from hello.models import Person, RequestLog, ModelChange


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
        self.assertIn('1997-09-16', response.content)
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

    fixtures = ['initial_data.json']

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
        jsoned_reqs = serializers.serialize('json', requests)
        self.assertEqual(jsoned_reqs, response.content)

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


class LogTest(TestCase):

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.login(username='user',
                               password='user')

    @patch('hello.views.logger')
    def test_error_log(self, mock_logger):
        """
        Tests if failed form submition is logged"""

        data = {'first_name': '',
                'last_name': '',
                'email': '',
                'birth_date': ''}

        self.auth_client.post('/api/edit/', data)
        expected = u'Form submition failed. Fields: first_name: , '\
                   u'last_name: , birth_date: , biography: None, email:'\
                   u' , skype: None, jabber: None, other_contacts: None.'\
                   u' Errors: {"birth_date": ["This field is required."],'\
                   u' "first_name": ["This field is required."], '\
                   u'"last_name": ["This field is required."],'\
                   u' "email": ["This field is required."]}'
        mock_logger.info.assert_called_with(expected)

    @patch('hello.views.logger')
    def test_ok_log(self, mock_logger):
        """
        Tests if successful form submition is logged"""

        data = {'first_name': 'William',
                'last_name': 'Doe',
                'biography': '',
                'email': 'w@doe.com',
                'skype': '',
                'jabber': '',
                'other_contacts': '',
                'birth_date': '1999-01-01'}

        self.auth_client.post('/api/edit/', data)
        expected = u'Successfully submitted form. Fields:'\
                   u' first_name: William, last_name: Doe,'\
                   u' birth_date: 1999-01-01, biography: ,'\
                   u' email: w@doe.com, skype: , jabber: ,'\
                   u' other_contacts: '
        mock_logger.info.assert_called_with(expected)


class TagTest(TestCase):

    fixtures = ['initial_data.json']

    def setUp(self):
        self.template = '{% load hello_tags %}{% edit_link obj %}'

    def render_template(self, template, context=None):
        context = context or {}
        context = Context(context)
        return Template(template).render(context)

    def test_edit_link_error(self):
        """
        Tests whether passing wrong argument to tag raises ValueError"""

        with self.assertRaises(ValueError):
            self.render_template(self.template, {'obj': 'string'})

    def test_edit_link(self):
        """
        Tests whether tag renders right link"""

        p = Person.objects.first()
        rendered = self.render_template(self.template, {'obj': p})
        expected = '<a href="/admin/hello/person/1/">Edit (admin)</a>'
        self.assertIn(expected, rendered)


class CommandTest(TestCase):

    fixtures = ['initial_data.json']

    def get_err_output(self, output):
        return '\n'.join(
            'error: ' + line for line in output.split('\n')[:-1]) + '\n'

    def test_command_option(self):
        """
        Tests whether command 'models' works right with '--all' option"""

        args = []
        options = {'app': True}
        out, err = StringIO(), StringIO()
        call_command('models', *args, stdout=out, stderr=err, **options)
        expected = 'Person (count: 1)\n'\
                   'RequestLog (count: 10)\n'\
                   'ModelChange (count: 26)\n'
        err_expected = self.get_err_output(expected)
        self.assertEqual(expected, out.getvalue())
        self.assertEqual(err_expected, err.getvalue())

    def test_command_no_option(self):
        """
        Tests whether command 'models' works right"""
        args = []
        options = {'app': False}
        out, err = StringIO(), StringIO()
        call_command('models', *args, stdout=out, stderr=err, **options)
        expected = 'Session (count: 0)\n'\
                   'LogEntry (count: 0)\n'\
                   'Permission (count: 30)\n'\
                   'Group (count: 0)\n'\
                   'User (count: 2)\n'\
                   'ContentType (count: 10)\n'\
                   'Person (count: 1)\n'\
                   'RequestLog (count: 10)\n'\
                   'ModelChange (count: 26)\n'\
                   'MigrationHistory (count: 0)\n'
        err_expected = self.get_err_output(expected)
        self.assertEqual(expected, out.getvalue())
        self.assertEqual(err_expected, err.getvalue())


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
        ModelChange(type='add',
                    model='Person',
                    instance_pk=1).save()
        new_count = ModelChange.objects.count()
        # if signal would create entry this would be at least 2
        self.assertEqual(new_count-old_count, 1)

    def test_ignore_edit(self):
        """
        Tests if changing instance of a model from ignore list
        would not create db entry"""

        old_count = ModelChange.objects.count()
        m = ModelChange.objects.first()
        m.instance_pk = ModelChange.objects.last().instance_pk
        m.save()
        new_count = ModelChange.objects.count()
        self.assertEqual(old_count, new_count)

    def test_ignore_delete(self):
        """
        Tests if deleting instance of a model from ignore list
        would not create db entry"""

        old_count = ModelChange.objects.count()
        ModelChange.objects.first().delete()
        new_count = ModelChange.objects.count()
        self.assertEqual(old_count-new_count, 1)
