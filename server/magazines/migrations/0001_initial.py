# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Magazine'
        db.create_table('magazines_magazine', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=4000, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('about', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('cover', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('magazines', ['Magazine'])

        # Adding model 'Category'
        db.create_table('magazines_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('magazines', ['Category'])

        # Adding model 'Issue'
        db.create_table('magazines_issue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('magazine', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['magazines.Magazine'])),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('magazines', ['Issue'])

        # Adding model 'Article'
        db.create_table('magazines_article', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('link', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['magazines.Issue'])),
            ('authors', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=10000, null=True, blank=True)),
        ))
        db.send_create_signal('magazines', ['Article'])

        # Adding M2M table for field category on 'Article'
        db.create_table('magazines_article_category', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article', models.ForeignKey(orm['magazines.article'], null=False)),
            ('category', models.ForeignKey(orm['magazines.category'], null=False))
        ))
        db.create_unique('magazines_article_category', ['article_id', 'category_id'])


    def backwards(self, orm):
        
        # Deleting model 'Magazine'
        db.delete_table('magazines_magazine')

        # Deleting model 'Category'
        db.delete_table('magazines_category')

        # Deleting model 'Issue'
        db.delete_table('magazines_issue')

        # Deleting model 'Article'
        db.delete_table('magazines_article')

        # Removing M2M table for field category on 'Article'
        db.delete_table('magazines_article_category')


    models = {
        'magazines.article': {
            'Meta': {'object_name': 'Article'},
            'authors': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['magazines.Category']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '10000', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['magazines.Issue']"}),
            'link': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'magazines.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'magazines.issue': {
            'Meta': {'object_name': 'Issue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'magazine': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['magazines.Magazine']"}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        'magazines.magazine': {
            'Meta': {'object_name': 'Magazine'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cover': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '4000', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['magazines']
