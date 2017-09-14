from django.shortcuts import render
from django.views import generic
from .models import Module, Student, Studying

class ModuleView(generic.ListView):
	template_name = 'Grades/modules.html'
	model = Module

	def get_queryset(self):
		return Module.objects.order_by('name')

class GradeView(generic.ListView):
	template_name = 'Grades/gradebook.html'
	model =  Module

	def get_context_data(self, **kwargs):
		context = super(ModuleView, self).get_context_data(**kwargs)
        
		for m_id in Module.objects.get(id=self.kwargs['pk']).module_ed_set.all()[:1]:
			sList = []
			gList = []
			for s_id in Module_ed.objects.get(id=m_id).studying_set.all():
				sList.append(Studying.objects.get(id=s_id).student_id)

			for c_id in Module_ed.objects.get(id=m_id).courses:
				for t_id in Course.objects.get(id=c_id).test_set.all():
					gList.append(Test.objects.get(id=t_id).grade_set.all())

		context['student_list'] = sList
		contest['grade_list'] = gList
		return context