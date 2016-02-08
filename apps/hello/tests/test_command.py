# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.management import call_command
from django.utils.six import StringIO
import os


class CommandTest(TestCase):

    fixtures = ['initial_data.json']

    def get_err_output(self, output):
        return '\n'.join(
            'error: ' + line for line in output.split('\n')[:-1]) + '\n'

    def test_command_app_option(self):
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

    def test_command_no_app_option(self):
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

    def test_command_file_option(self):
        """
        Tests wheter '-f' and '--file' options will log output to file"""

        args = []
        filename = 'log'
        options = {'filename': filename}
        # in order not to mess tests output:
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
        file_content = open(filename).read()
        self.assertEqual(expected, file_content)
        os.remove(filename)
