# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding M2M table for field similar on 'Book'
        db.create_table('book_book_similar', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_book', models.ForeignKey(orm['book.book'], null=False)),
            ('to_book', models.ForeignKey(orm['book.book'], null=False))
        ))
        db.create_unique('book_book_similar', ['from_book_id', 'to_book_id'])


    def backwards(self, orm):
        
        # Removing M2M table for field similar on 'Book'
        db.delete_table('book_book_similar')


    models = {
        'book.annotation': {
            'Meta': {'object_name': 'Annotation'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['book.Book']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {})
        },
        'book.author': {
            'Meta': {'object_name': 'Author'},
            'alias': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['book.AuthorAlias']", 'null': 'True', 'blank': 'True'}),
            'credit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'tag': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['book.Tag']", 'null': 'True', 'blank': 'True'})
        },
        'book.authoralias': {
            'Meta': {'object_name': 'AuthorAlias'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'book.book': {
            'Meta': {'object_name': 'Book'},
            'author': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['book.Author']", 'null': 'True', 'blank': 'True'}),
            'book_file': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['book.BookFile']", 'null': 'True', 'blank': 'True'}),
            'credit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['book.Language']"}),
            'pagelink': ('django.db.models.fields.TextField', [], {'max_length': '4000', 'null': 'True', 'blank': 'True'}),
            'series': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['book.Series']", 'null': 'True', 'blank': 'True'}),
            'similar': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'similar_rel_+'", 'null': 'True', 'to': "orm['book.Book']"}),
            'tag': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['book.Tag']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'book.bookfile': {
            'Meta': {'object_name': 'BookFile'},
            'credit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_link': ('django.db.models.fields.TextField', [], {'max_length': '4000', 'null': 'True', 'blank': 'True'}),
            'last_check': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.TextField', [], {'max_length': '4000'}),
            'link_hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'more_info': ('django.db.models.fields.TextField', [], {'max_length': '10000', 'null': 'True', 'blank': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'time_found': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'book.epubbook': {
            'Meta': {'object_name': 'EpubBook'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['book.Book']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'book.language': {
            'Meta': {'object_name': 'Language'},
            'full': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'full_national': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2'})
        },
        'book.series': {
            'Meta': {'object_name': 'Series'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'book.tag': {
            'Meta': {'object_name': 'Tag'},
            'credit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['book.Tag']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['book']
