# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Refresh'
        db.create_table('analyser_app_refresh', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('link', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('analyser_app', ['Refresh'])


    def backwards(self, orm):
        
        # Deleting model 'Refresh'
        db.delete_table('analyser_app_refresh')


    models = {
        'analyser_app.refresh': {
            'Meta': {'object_name': 'Refresh'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {}),
            'link': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
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
