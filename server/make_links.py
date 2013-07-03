import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.conf import settings
from urllib import quote
from book.models import Book
from book.models import BookFile

all_books = Book.objects.filter(book_file__link__contains="http://lib.ru")

for book in all_books:
    book_files = BookFile.objects.filter(link__contains="from/lib/ru/?link=")
    for book_file in book_files:
        book_file.delete()