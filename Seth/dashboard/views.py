from django.shortcuts import render
from django.contrib.auth.decorators import permission_required


@permission_required('grades.add_grade')
def home(request):
    context = dict()
    return render(request, 'dashboard/index.html', context)
