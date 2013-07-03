# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'BookFile'
        db.create_table('book_bookfile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('link', self.gf('django.db.models.fields.TextField')(max_length=4000)),
            ('link_hash', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('time_found', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_check', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('size', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('more_info', self.gf('django.db.models.fields.TextField')(max_length=10000, null=True, blank=True)),
            ('img_link', self.gf('django.db.models.fields.TextField')(max_length=4000, null=True, blank=True)),
            ('credit', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('book', ['BookFile'])

        # Adding model 'Series'
        db.create_table('book_series', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('book', ['Series'])

        # Adding model 'AuthorAlias'
        db.create_table('book_authoralias', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('book', ['AuthorAlias'])

        # Adding model 'Tag'
        db.create_table('book_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('book', ['Tag'])

        # Adding model 'Language'
        db.create_table('book_language', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short', self.gf('django.db.models.fields.CharField')(unique=True, max_length=2)),
            ('full', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('full_national', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('book', ['Language'])

        # Adding model 'Author'
        db.create_table('book_author', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('credit', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('book', ['Author'])

        # Adding M2M table for field alias on 'Author'
        db.create_table('book_author_alias', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('author', models.ForeignKey(orm['book.author'], null=False)),
            ('authoralias', models.ForeignKey(orm['book.authoralias'], null=False))
        ))
        db.create_unique('book_author_alias', ['author_id', 'authoralias_id'])

        # Adding M2M table for field tag on 'Author'
        db.create_table('book_author_tag', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('author', models.ForeignKey(orm['book.author'], null=False)),
            ('tag', models.ForeignKey(orm['book.tag'], null=False))
        ))
        db.create_unique('book_author_tag', ['author_id', 'tag_id'])

        # Adding model 'Book'
        db.create_table('book_book', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('lang', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['book.Language'])),
            ('credit', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('pagelink', self.gf('django.db.models.fields.TextField')(max_length=4000, null=True, blank=True)),
        ))
        db.send_create_signal('book', ['Book'])

        # Adding M2M table for field book_file on 'Book'
        db.create_table('book_book_book_file', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('book', models.ForeignKey(orm['book.book'], null=False)),
            ('bookfile', models.ForeignKey(orm['book.bookfile'], null=False))
        ))
        db.create_unique('book_book_book_file', ['book_id', 'bookfile_id'])

        # Adding M2M table for field series on 'Book'
        db.create_table('book_book_series', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('book', models.ForeignKey(orm['book.book'], null=False)),
            ('series', models.ForeignKey(orm['book.series'], null=False))
        ))
        db.create_unique('book_book_series', ['book_id', 'series_id'])

        # Adding M2M table for field tag on 'Book'
        db.create_table('book_book_tag', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('book', models.ForeignKey(orm['book.book'], null=False)),
            ('tag', models.ForeignKey(orm['book.tag'], null=False))
        ))
        db.create_unique('book_book_tag', ['book_id', 'tag_id'])

        # Adding M2M table for field author on 'Book'
        db.create_table('book_book_author', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('book', models.ForeignKey(orm['book.book'], null=False)),
            ('author', models.ForeignKey(orm['book.author'], null=False))
        ))
        db.create_unique('book_book_author', ['book_id', 'author_id'])

        # Adding model 'EpubBook'
        db.create_table('book_epubbook', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['book.Book'])),
        ))
        db.send_create_signal('book', ['EpubBook'])

        # Adding model 'Annotation'
        db.create_table('book_annotation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['book.Book'])),
        ))
        db.send_create_signal('book', ['Annotation'])


    def backwards(self, orm):
        
        # Deleting model 'BookFile'
        db.delete_table('book_bookfile')

        # Deleting model 'Series'
        db.delete_table('book_series')

        # Deleting model 'AuthorAlias'
        db.delete_table('book_authoralias')

        # Deleting model 'Tag'
        db.delete_table('book_tag')

        # Deleting model 'Language'
        db.delete_table('book_language')

        # Deleting model 'Author'
        db.delete_table('book_author')

        # Removing M2M table for field alias on 'Author'
        db.delete_table('book_author_alias')

        # Removing M2M table for field tag on 'Author'
        db.delete_table('book_author_tag')

        # Deleting model 'Book'
        db.delete_table('book_book')

        # Removing M2M table for field book_file on 'Book'
        db.delete_table('book_book_book_file')

        # Removing M2M table for field series on 'Book'
        db.delete_table('book_book_series')

        # Removing M2M table for field tag on 'Book'
        db.delete_table('book_book_tag')

        # Removing M2M table for field author on 'Book'
        db.delete_table('book_book_author')

        # Deleting model 'EpubBook'
        db.delete_table('book_epubbook')

        # Deleting model 'Annotation'
        db.delete_table('book_annotation')


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
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['book.Language']"}),
            'pagelink': ('django.db.models.fields.TextField', [], {'max_length': '4000', 'null': 'True', 'blank': 'True'}),
            'series': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['book.Series']", 'null': 'True', 'blank': 'True'}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['book']
