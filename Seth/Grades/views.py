from django.shortcuts import render
from django.views import generic
from .models import Module, Studying, Module_ed, Course, Test, Grade

class ModuleView(generic.ListView):
	template_name = 'Grades/modules.html'
	model = Module

	def get_queryset(self):
		return Module.objects.order_by('name')

class GradeView(generic.DetailView):
	template_name = 'Grades/gradebook.html'
	model = Module

	def get_context_data(self, **kwargs):
		context = super(GradeView, self).get_context_data(**kwargs)
        
		dList = []
		tList = []
		courseDict = dict()
		testDict = dict()

		m_id = Module_ed.objects.get(module=self.kwargs['pk'])
		for studying in Studying.objects.all().filter(module_id=m_id):
			studentDict = dict()

			studentDict['id'] = studying.student_id
			studentDict['user'] = studying.student_id.user
			print(studying.student_id.user)
			for course in m_id.courses.all():

				tList = []
				if course.id not in courseDict.keys():
					courseDict[course.id] = course.name

				for test in Test.objects.all().filter(course_id=course):

					if test not in tList:
						tList.append(test)

					for grade in Grade.objects.all().filter(student_id=studying.student_id).filter(test_id=test):
						studentDict[test.id] = grade.grade
					testDict[course.id] = tList

			dList.append(studentDict)

		context['studentdict'] = dList
		context['coursedict'] = courseDict
		context['testdict'] = testDict
		return context

class StudentView(generic.DetailView):
	template_name = 'Grades/student.html'
	model = Course

	def get_context_data(self, **kwargs):
		context = super(StudentView, self).get_context_data(**kwargs)

		mod = Module_ed.objects.get(module=self.kwargs['pk'])
		stu = Student.objects.get(student_id=self.kwargs['sid'])

		tList = []
		courseDict = dict()
		testDict = dict()
		gradeDict = dict()

		for course in mod.courses.all():
			tList = []

			if course.id not in courseDict.keys():
				courseDict[course.id] = course.name	

			for test in Test.objects.all().filer(course_id=course):

				if test not in tList:
					tList.append(test)

				for grade in Grade.objects.all().filter(student_id=studying.student_id).filter(test_id=test):
					gradeDict[test.id] = grade.grade

				testDict[course.id] = tList

		context['student'] = stu
		context['user'] = stu.user
		context['coursedict'] = courseDict
		context['testdict'] = testDict
		context['gradedict'] = gradeDict

