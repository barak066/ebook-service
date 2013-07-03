
from south.db import db
from django.db import models
from server.reader.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'PrivateContent'
        db.create_table('reader_privatecontent', (
            ('id', orm['reader.PrivateContent:id']),
            ('private_content', orm['reader.PrivateContent:private_content']),
        ))
        db.send_create_signal('reader', ['PrivateContent'])
        
        # Adding model 'PublicContent'
        db.create_table('reader_publiccontent', (
            ('id', orm['reader.PublicContent:id']),
            ('public_content', orm['reader.PublicContent:public_content']),
        ))
        db.send_create_signal('reader', ['PublicContent'])
        
        # Adding model 'Request'
        db.create_table('reader_request', (
            ('id', orm['reader.Request:id']),
            ('request', orm['reader.Request:request']),
            ('request_hash', orm['reader.Request:request_hash']),
        ))
        db.send_create_signal('reader', ['Request'])
        
        # Adding model 'OpenID'
        db.create_table('reader_openid', (
            ('id', orm['reader.OpenID:id']),
            ('open_id', orm['reader.OpenID:open_id']),
        ))
        db.send_create_signal('reader', ['OpenID'])
        
        # Adding ManyToManyField 'OpenID.request'
        db.create_table('reader_openid_request', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('openid', models.ForeignKey(orm.OpenID, null=False)),
            ('request', models.ForeignKey(orm.Request, null=False))
        ))
        
        # Adding ManyToManyField 'OpenID.private_content'
        db.create_table('reader_openid_private_content', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('openid', models.ForeignKey(orm.OpenID, null=False)),
            ('privatecontent', models.ForeignKey(orm.PrivateContent, null=False))
        ))
        
        # Adding ManyToManyField 'OpenID.public_content'
        db.create_table('reader_openid_public_content', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('openid', models.ForeignKey(orm.OpenID, null=False)),
            ('publiccontent', models.ForeignKey(orm.PublicContent, null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'PrivateContent'
        db.delete_table('reader_privatecontent')
        
        # Deleting model 'PublicContent'
        db.delete_table('reader_publiccontent')
        
        # Deleting model 'Request'
        db.delete_table('reader_request')
        
        # Deleting model 'OpenID'
        db.delete_table('reader_openid')
        
        # Dropping ManyToManyField 'OpenID.request'
        db.delete_table('reader_openid_request')
        
        # Dropping ManyToManyField 'OpenID.private_content'
        db.delete_table('reader_openid_private_content')
        
        # Dropping ManyToManyField 'OpenID.public_content'
        db.delete_table('reader_openid_public_content')
        
    
    
    models = {
        'reader.openid': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'open_id': ('django.db.models.fields.TextField', [], {'max_length': '4000'}),
            'private_content': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['reader.PrivateContent']"}),
            'public_content': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['reader.PublicContent']"}),
            'request': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['reader.Request']"})
        },
        'reader.privatecontent': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'private_content': ('django.db.models.fields.TextField', [], {'max_length': '10000'})
        },
        'reader.publiccontent': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'public_content': ('django.db.models.fields.TextField', [], {'max_length': '10000'})
        },
        'reader.request': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'request': ('django.db.models.fields.TextField', [], {'max_length': '4000'}),
            'request_hash': ('django.db.models.fields.CharField', [], {'max_length': '32', 'unique': 'True'})
        }
    }
    
    complete_apps = ['reader']
