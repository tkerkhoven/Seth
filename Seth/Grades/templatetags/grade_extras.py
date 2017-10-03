from django import template

register = template.Library()

@register.filter(name='key')
def key(d, key_name):
    try:
        value = d[key_name]
    except:
        value = 'N/A'

    return value

@register.filter(name='grade_od')
def gradeordash(d):
    try:
        value = round(d.grade,1)

    except:
        value = '-'

    return value

@register.filter(name='grade_od_no_round')
def gradeordash_nr(d):
    try:
        value = d.grade

    except:
        value = '-'

    return value

@register.filter(name='round')
def g_round(d):
    try:
        value = round(d,1)
    except:
        value = '-'

    return value

@register.filter(name='study_od')
def studyordash(d):
    try:
        value = d.full_name + " " + d.short_name

    except:
        value = '-'

    return value

@register.filter(name='iseven')
def iseven(d):
    try:
        value = d % 2
    except:
        value = 'N/A'
    print(d)
    return (value == 0)