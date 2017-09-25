from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.http import Http404
from Grades.models import Module_ed, Test
from django.utils import timezone

# @permission_required('grades.add_grade')
def home(request):

    context = dict()
    module_eds = get_module_eds()

    context['modules'] = []
    for module in module_eds:
        courses = []

        for course in module.courses.all():
            courses.append({
                'name': course.name,
                'pk': course.pk,
                'tests': Test.objects.filter(course_id=course.pk),
            })
        context['modules'].append({
            'name': module.module.name,
            'courses': courses,
            'active': (module.start <= timezone.now().date() <= module.stop)

        })

    return render(request, 'dashboard/index.html', context)


def settings(request):
    raise Http404('Settings unimplemented')


def get_module_eds():
    return Module_ed.objects.order_by('start')