import sys
import os

sys.path.insert(1,'../')
sys.path.insert(2,'../server/')

#print sys.path

#using proxy for connection if necessary:
os.environ['http_proxy'] = 'http://192.168.0.2:3128/'

#for using django ORM:
from django.core.management import setup_environ
from server import settings
setup_environ(settings)
