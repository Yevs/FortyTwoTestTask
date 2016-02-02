from __future__ import unicode_literals
from django.db import models


class Person(models.Model):
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    birth_date = models.DateField()
    biography = models.TextField(blank=True)
    email = models.EmailField()
    skype = models.CharField(max_length=40, blank=True)
    jabber = models.CharField(max_length=40, blank=True)
    other_contacts = models.TextField(blank=True)

    def __unicode__(self):
        return self.first_name + ' ' + self.last_name


class RequestLog(models.Model):
    datetime = models.DateTimeField(blank=False, auto_now_add=True)
    method = models.CharField(blank=False, max_length=40)
    path = models.CharField(blank=False, max_length=40)

    def __unicode__(self):
        return \
            self.datetime.strftime('%d/%b/%Y %H:%M') +\
            ' ' + self.method + ' ' + self.path
