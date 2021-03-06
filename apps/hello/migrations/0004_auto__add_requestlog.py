# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RequestLog'
        db.create_table(u'hello_requestlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal(u'hello', ['RequestLog'])



    def backwards(self, orm):
        # Deleting model 'RequestLog'
        db.delete_table(u'hello_requestlog')


    models = {
        u'hello.person': {
            'Meta': {'object_name': 'Person'},
            'biography': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'birth_date': ('django.db.models.fields.DateField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jabber': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'other_contacts': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'skype': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        },
        u'hello.requestlog': {
            'Meta': {'object_name': 'RequestLog'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        }
    }

    complete_apps = ['hello']