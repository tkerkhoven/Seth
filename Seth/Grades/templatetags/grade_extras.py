from django import template

register = template.Library()

@register.filter(name='key')
def key(d, key_name):
    try:
        value = d[key_name]
    except:
        from django.conf import settings
        value = 'N/A'

    return value