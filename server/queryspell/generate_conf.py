import os

from django.template import Context, Template

import settings
from queryspell.models import Dictionary, Words

def generate_sphinx_conf(only_index=False):
    path = os.path.join(os.path.dirname(__file__), 'templates/')
    name = 'sphinx.conf'


    dictionaries = Dictionary.objects.all()

    try:
        fp = open(path + name, 'r')
        template = Template(fp.read())
        dict_id_column = \
            (x for x in Words._meta.fields if x.name == 'dictionary').next()

        context = {
            'table_name': Words._meta.db_table,
            'dict_id_column': dict_id_column.column,
            'index': getattr(settings, 'QUERYSPELL_INDEX', 'queryspell_index'),
            'only_index': only_index,
        }
        context.update({
            'SPHINX_HOST': getattr(settings, 'SPHINX_HOST', '127.0.0.1'),
            'SPHINX_PORT': getattr(settings, 'SPHINX_PORT', '3312'),
    
            'SPHINX_LOG_PATH': \
                os.path.abspath(getattr(settings, 'SPHINX_LOG_PATH', '/var/log')),
            'SPHINX_INDEX_PATH': \
                os.path.abspath(getattr(settings, 'SPHINX_INDEX_PATH', \
                                        '/var/data')),
        })
        if getattr(settings, 'DATABASES', None):
            context.update({
                'DATABASE_ENGINE': settings.DATABASES['default']['ENGINE'],
                'DATABASE_HOST': settings.DATABASES['default']['HOST'],
                'DATABASE_PASSWORD': settings.DATABASES['default']['PASSWORD'],
                'DATABASE_USER': settings.DATABASES['default']['USER'],
                'DATABASE_PORT': settings.DATABASES['default']['PORT'],
                'DATABASE_NAME': settings.DATABASES['default']['NAME'],
            })
        else:
            context.update({
                'DATABASE_ENGINE': settings.DATABASE_ENGINE,
                'DATABASE_HOST': settings.DATABASE_HOST,
                'DATABASE_PASSWORD': settings.DATABASE_PASSWORD,
                'DATABASE_USER': settings.DATABASE_USER,
                'DATABASE_PORT': settings.DATABASE_PORT,
                'DATABASE_NAME': settings.DATABASE_NAME,
            })

        fp.close()
        return template.render(Context(context))
    except IOError, ex:
        raise ValueError, "Template matching name does not exist: %s." % (name,)


