# Django settings for server project.
import os.path
import os
try:
    os.environ['PYTHONPATH'] += ':..'
except KeyError:
    os.environ['PYTHONPATH'] = '..'

import sys
sys.path.append('..')
from django.utils.version import *
DEBUG = False
TEMPLATE_DEBUG = DEBUG
APPEND_SLASH = True

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'project2'             # Or path to database file if using sqlite3.
DATABASE_USER = 'user2'             # Not used with sqlite3.
#DATABASE_PASSWORD = 'betaP2'         # Not used with sqlite3.
#DATABASE_HOST = '192.168.216.133'             # Set to empty string for localhost. Not used with sqlite3.
#DATABASE_PORT = '3306'             # Set to empty string for default. Not used with sqlite3.
#DATABASE_HOST = 'localhost'             # Set to empty string for localhost. Not used with sqlite3.
#DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Moscow'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html

_ = lambda s: s

LANGUAGES = (
      ('ru', _('Russian')),
      ('en', _('English')),
)
USE_AUTOCOMPLETE = False

LANGUAGE_CODE = 'en-us'
#LANGUAGE_CODE = 'ru'
SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = 'media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'media'
MEDIA_DOWNLOAD_FOLDER='downloads'
EPUB_URL = 'epub_media' #made for distribution for apache, because nginx doesn't set mime-type for *.epub

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

ugettext = lambda s: s
LOGIN_URL = '/%s%s' % (ugettext('account/'), ugettext('signin/'))

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'v_%-@z3(t6y!1a3m$s7ulv9#&@e6_e-m_rk9v5&&9gj&+ug9e$'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'localeurl.middleware.LocaleURLMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.transaction.TransactionMiddleware',
    
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    'django.middleware.doc.XViewMiddleware',
    'spec.external.pagination.middleware.PaginationMiddleware',
    'django.middleware.cache.CacheMiddleware',
    #'django.middleware.locale.LocaleMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware',

#    'django_authopenid.middleware.OpenIDMiddleware',
)
#    'django.middleware.common.CommonMiddleware',

CACHE_MIDDLEWARE_SECONDS = 1
CACHE_MIDDLEWARE_KEY_PREFIX = ''

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
#    'ebooks/templates',
#    'templates',
    os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),

#    '/home/geometer/ebooksearch/server/templates',
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'localeurl',
    'django.contrib.auth',
	'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',

    'django.contrib.admin',
#    'django.contrib.admindocs',
    'book',
    'magazines',
    'analyser_app',
   # 'reader',
    'tests',
    'djangosphinx',
    'spec.external.pagination',
#    'queryspell',
    #openid
#    'django_authopenid',
    'indexer',
    'paging',
    'sentry',
    'sentry.client',
    'south',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",

)

TEST_RUNNER = 'test_runner.run_tests'

# path to log file
LOG_FILENAME = 'main.log'

MAX_LOG_SIZE = 1024*1000
BACKUP_COUNT = 10

# analyzer ip
# set ANALYZER_IP='', if you don't need to check it
ANALYZER_IP = ''#'192.168.211.26'

# ebst server version
EBST_VERSION = '0.1'
EBST_VERSION_BUILD = get_svn_revision('/home/ebooksearch/webapps/ebook_service/service')[4:]
# ebst server name
EBST_NAME = 'eBookSearchServer'

# root url
#ROOT_URL = r'^ebooks/'


# search engine settings
# Sphinx 0.9.9
SPHINX_API_VERSION = 0x116

#SPHINX_CONF_DIR = "spec"
#SPHINX_CONF_FILE = "sphinx.conf"

#SPHINX_LOG_PATH = '/var/log'
#SPHINX_INDEX_PATH = '/var/data'

#SPHINX_HOST = '127.0.0.1'
#SPHINX_PORT = '3321'

# debug settings
# show django exception in response
#ANALYZER_DEBUG_MODE = True

# Analyzer setting
ANALYZER_DEFAULT_RESULT_LENGTH = 5


# Search engine
# Max result length
MAX_RESULT_LENGTH = 200

# Path to aspell dictionaries
#ASPELL_DICTIONARIES = '/usr/lib/aspell-0.60'

FILE_UPLOAD_PERMISSIONS = 0644

RESULTS_PER_PAGE = 20

import re
LOCALE_INDEPENDENT_PATHS = (
    re.compile('^/i18n/'),
    re.compile('^/css/'),
    re.compile('^/images/'),
    re.compile('^/js/'),
    re.compile('^/ajax/'),
)

LOCALEURL_USE_ACCEPT_LANGUAGE = True

try:
    from local_settings import *
except Exception:
    pass

