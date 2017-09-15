from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.http import Http404
from Grades.models import Module, Course

# @permission_required('grades.add_grade')
def home(request):
    context = {
         'modules': get_modules()
        # [
        #     {
        #         'name': 'Pearls of Computer Science',
        #         'courses': [
        #             {
        #                 'name': 'Pearl 1',
        #             }
        #         ]
        #     }
        # ],
    }
    return render(request, 'dashboard/index.html', context)


def settings(request):
    raise Http404('Settings unimplemented')


def get_modules():
    return Module.objects.order_by('start')