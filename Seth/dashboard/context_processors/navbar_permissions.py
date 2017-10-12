from Grades.models import Coordinator


def permissions(request):

    if not request.user.is_anonymous() and Coordinator.objects.filter(person__user=request.user):

        return {'module_coordinator': True}
    else:
        return {'module_coordinator:': False}
