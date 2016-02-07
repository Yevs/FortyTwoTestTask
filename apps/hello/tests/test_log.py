# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test import Client
from mock import patch


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
