# -*- coding: utf-8 -*-
from django.test import TestCase
from django.template import Context, Template
from hello.models import Person


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
        expected = '/admin/hello/person/1/'
        self.assertEqual(expected, rendered)
