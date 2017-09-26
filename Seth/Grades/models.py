import datetime

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone


####################################################################
###############          Independent Models          ###############
####################################################################


class Module(models.Model):
    module_code = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=32)
    start = models.DateField(default=datetime.date(1, 1, 1))
    stop = models.DateField(default=datetime.date(9999, 12, 31))

    def __str__(self):
        return '{} ({})'.format(self.name, self.module_code)


# class Student(models.Model):
#     student_id = models.CharField(primary_key=True, max_length=16)

#     user = models.ForeignKey(User, blank=True, null=True)

#     def __str__(self):
#         return '{} ({})'.format(self.user.username, self.student_id)


####################################################################
###############          Dependent Models 1          ###############
####################################################################

class Study(models.Model):
    short_name = models.CharField(primary_key=True, max_length=10)
    modules = models.ManyToManyField(Module)

    full_name = models.CharField(max_length=32, null=True)

    def __str__(self):
        return self.full_name


class Person(models.Model):
    name = models.CharField(max_length=32)
    id_prefix = models.CharField(max_length=8)
    person_id = models.CharField(max_length=16)
    user = models.ForeignKey(User, blank=True,
                             null=True)  # ToDo: vm is dit de Django-user, is dit nodig voor elke Person?
    start = models.DateField(default=datetime.date(1, 1, 1))
    stop = models.DateField(default=datetime.date(9999, 12, 31))
    ROLES = (
        ('T', 'Teacher'),
        ('S', 'Student'),
        ('A', 'Teaching Assistant'),
        ('V', 'Study Advisor')
    )
    role = models.CharField(max_length=1, choices=ROLES)

    # Iff role == 'V'
    studies = models.ManyToManyField(Study)

    @property
    def full_id(self):
        return self.id_prefix + self.person_id

    def __str__(self):
        return '{} ({})\t\t{}'.format(self.name, self.full_id, self.role)


# class Teacher(models.Model):
#     employee_id = models.CharField(blank=True, null=True, max_length=16)
#     student_id = models.ForeignKey(Student, blank=True, null=True)


#     user = models.ForeignKey(User, blank=True, null=True)

#     TEACHER_OPTIONS = (             # Defaults to Teaching Assistant
#             ('T', 'Teacher'),
#             ('A', 'Teaching Assistant'),
#         )

#     job = models.CharField(max_length=1, choices=TEACHER_OPTIONS)

#     def __str__(self):
#         if self.user:
#             return '{} ({})'.format(self.user.username, self.job)
#         else:
#             return '{} ({})'.format(self.student_id.user.username, self.job)

####################################################################
###############          Dependent Models 2          ###############
####################################################################

class Course(models.Model):
    code = models.CharField(max_length=16, default='')
    code_extension = models.CharField(max_length=16, default='')
    teachers = models.ManyToManyField(Person)

    name = models.CharField(max_length=32, null=True)

    @property
    def course_code(self):
        return self.code + self.code_extension

    def get_absolute_url(self):
        return reverse('module_management:course_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '{} ({})'.format(self.name, self.course_code)


class Module_ed(models.Model):
    year = models.DateField(default=timezone.now)
    module = models.ForeignKey(Module)
    module_code_extension = models.CharField(max_length=16, default='')

    courses = models.ManyToManyField(Course)
    module_coordinator = models.ManyToManyField(Person)

    start = models.DateField(default=datetime.date(1, 1, 1))
    stop = models.DateField(default=datetime.date(9999, 12, 31))

    @property
    def module_code(self):
        return str(self.year.year) + self.module.module_code + self.module_code_extension

    def get_absolute_url(self):
        return reverse('module_management:module_ed_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '{} ({}) ({} - {})'.format(self.module, self.module_code, self.start, self.stop)


# class Advisor(models.Model):
#     studies = models.ManyToManyField(Study)
#     employee_id = models.CharField(primary_key=True, max_length=16)
#     user = models.ForeignKey(User, blank=True, null=True)

#     start = models.DateField(default=datetime.date(1,1,1))
#     stop = models.DateField(default=datetime.date(1,1,1))

#     def __str__(self):
#         return self.name

####################################################################
###############          Dependent Models 3          ###############
####################################################################

class Test(models.Model):
    course_id = models.ForeignKey(Course, related_name='coursebacktable')

    name = models.CharField(max_length=32, null=True)
    # Update TEST_TYPES in @property:get_type()
    TEST_TYPES = (  # Defaults to Exam
        ('E', 'Exam'),
        ('A', 'Assignment'),
        ('P', 'Project')
    )
    _type = models.CharField(max_length=1, choices=TEST_TYPES)
    time = models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0, 0, 0))

    maximum_grade = models.DecimalField(max_digits=6, decimal_places=3, default=10.0)
    minimum_grade = models.DecimalField(max_digits=6, decimal_places=3, default=1.0)

    def __str__(self):
        return '{} ({}) {}'.format(self.name, self._type, self.time)

    # Should be the same as TEST_TYPES
    @property
    def get_type(self):
        return {
            'E': 'Exam',
            'A': 'Assignment',
            'P': 'Project'
        }[self._type]

    def get_absolute_url(self):
        return reverse('module_management:test_detail', kwargs={'pk': self.pk})


class Studying(models.Model):
    student_id = models.ForeignKey(Person)
    study = models.ForeignKey(Study)
    module_id = models.ForeignKey(Module_ed)
    role = models.CharField(max_length=32)


class Criterion(models.Model):
    study = models.ForeignKey(Study)
    module_id = models.ForeignKey(Module_ed)
    condition = models.CharField(max_length=32)
    role = models.CharField(max_length=32)

    def __str__(self):
        return self.condition


####################################################################
###############          Dependent Models 4          ###############
####################################################################

class Grade(models.Model):
    test_id = models.ForeignKey(Test)
    teacher_id = models.ForeignKey(Person, related_name='Correcter')
    student_id = models.ForeignKey(Person, related_name='Submitter')
    time = models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0, 0, 0))
    description = models.CharField(max_length=256, null=True)
    grade = models.DecimalField(max_digits=6, decimal_places=3, default=1.0)
    released = models.BooleanField(default=False)

    def __str__(self):
        return self.grade.__str__()
