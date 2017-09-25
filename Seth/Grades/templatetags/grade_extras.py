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

@register.filter(name='grade_od')
def gradeordash(d):
    try:
        value = d.grade
    except:
        from django.conf import settings
        value = '-'

    return value