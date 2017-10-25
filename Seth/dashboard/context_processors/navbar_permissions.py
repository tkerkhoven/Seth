from Grades.models import Coordinator, Teacher, Study


def permissions(request):

    # if not request.user.is_anonymous() and Coordinator.objects.filter(person__user=request.user):
    #
    #     return {'module_coordinator': True}
    # else:
    #     return {'module_coordinator:': False}
    context = dict()

    if not request.user.is_anonymous():
        context['is_module_coordinator'] = False
        context['is_teacher'] = False
        context['is_ta'] = False
        context['is_mc_assistant'] = False
        context['is_adviser'] = False
        if Coordinator.objects.filter(person__user=request.user):
            context['is_module_coordinator'] = True
        if Teacher.objects.filter(person__user=request.user).filter(role='T'):
            context['is_teacher'] = True
        if Teacher.objects.filter(person__user=request.user).filter(role='A'):
            context['is_teacher'] = True
            context['is_ta'] = True
        if Coordinator.objects.filter(person__user=request.user).filter(is_assistant=True):
            context['is_mc_assistant'] = True
        if Study.objects.filter(advisers__user=request.user):
            context['is_adviser'] = True
    return context
