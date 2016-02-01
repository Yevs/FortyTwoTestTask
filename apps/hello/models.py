from __future__ import unicode_literals
from django.db import models
from PIL import Image
import uuid
import os


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('avatars/', filename)


class Person(models.Model):
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    birth_date = models.DateField()
    biography = models.TextField(blank=True)
    email = models.EmailField()
    skype = models.CharField(max_length=40, blank=True)
    jabber = models.CharField(max_length=40, blank=True)
    other_contacts = models.TextField(blank=True)
    avatar = models.ImageField(upload_to=get_file_path,
                               default='avatars/default.png')

    def save(self, *args, **kwargs):
        try:
            this = Person.objects.get(id=self.id)
            if this.avatar != self.avatar and\
               'default.png' not in str(this.avatar):
                this.avatar.delete(save=False)
        except:
            pass  # new photo

        super(Person, self).save(*args, **kwargs)

        if self.avatar:
            size = 200, 200
            image = Image.open(self.avatar.path)
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(self.avatar.path)

    def __unicode__(self):
        return self.first_name + ' ' + self.last_name


class RequestLog(models.Model):
    datetime = models.DateTimeField(blank=False)
    method = models.CharField(blank=False, max_length=40)
    path = models.CharField(blank=False, max_length=40)

    def __unicode__(self):
        return \
            self.datetime.strftime('%d/%b/%Y %H:%M') +\
            ' ' + self.method + ' ' + self.path
