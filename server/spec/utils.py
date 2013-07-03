from string import join, split

from django.core.exceptions import ObjectDoesNotExist

from book.models import Language

def convert_delim(strs, delimiter=' '):
    '''Convert all \\r \\n \\t to delimiter.
       Input parametr: strs is one string or list of strings'''
    if isinstance(strs, list):
        result = map(lambda x: join(split(x), delimiter), strs)
    else:
        result = join(split(strs), delimiter)
    return result


def replace_delim_to_space(str, delimiter=' '):
    if str:
        return join(split(str), delimiter)
    return ''


def get_language(lang_code):
    """
    Gets language objects by short code or full name.
    Returns it, or 'unknown' language if not found.
    """
    language = None
    try:
        if lang_code:
            if len(lang_code) == 2:
                language = Language.objects.get(short=lang_code.lower())
            else:
                language = Language.objects.get(full=lang_code)
    except ObjectDoesNotExist:
        language = None
    
    if not language:
        language = Language.objects.get(short='?')
    return language
