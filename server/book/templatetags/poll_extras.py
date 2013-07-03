import urllib
from django.template.defaultfilters import stringfilter
from django import template

register = template.Library()

@register.filter(name="quote")
@stringfilter
def quote(value):
    temp = value[:]
    try:
        temp = temp.encode("utf-8")
    except:
        pass
    return urllib.quote(temp)
