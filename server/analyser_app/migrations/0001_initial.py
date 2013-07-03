# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Task'
        db.create_table('analyser_app_task', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('serialized_task', self.gf('analyser_app.picklefield.fields.PickledObjectField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('parser_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('weight', self.gf('django.db.models.fields.IntegerField')()),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=4000, null=True, blank=True)),
            ('good', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('reason', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('analyser_app', ['Task'])


    def backwards(self, orm):
        
        # Deleting model 'Task'
        db.delete_table('analyser_app_task')


    models = {
        'analyser_app.task': {
            'Meta': {'object_name': 'Task'},
            'good': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '4000', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parser_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'reason': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'serialized_task': ('analyser_app.picklefield.fields.PickledObjectField', [], {}),
            'weight': ('django.db.models.fields.IntegerField', [], {}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['analyser_app']
