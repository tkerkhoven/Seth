from django.db import models
import datetime

####################################################################
###############          Independent Models          ###############
####################################################################

class Module(models.Model):

    name = models.CharField(max_length=32)
    start = models.DateField()  # Defaults to earliest date possible
    stop = models.DateField()   # Defaults to earliest date possible


class Student(models.Model):
    _id = models.CharField(primary_key=True, max_length=16)

    name = models.CharField(max_length=32, null=True)
    mail = models.CharField(max_length=32, null=True)


####################################################################
###############          Dependent Models 1          ###############
####################################################################

class Study(models.Model):
    short_name = models.CharField(primary_key=True, max_length=10)
    modules = models.ManyToManyField(Module)

    full_name = models.CharField(max_length=32, null=True)

class Teacher(models.Model):
    teacher_id = models.CharField(primary_key=True, max_length=16)
    student_id = models.ForeignKey(Student)

    name = models.CharField(max_length=32, null=True)
    mail = models.CharField(max_length=32, null=True)

    TEACHER_OPTIONS = (             # Defaults to Teaching Assistant
            ('T', 'Teacher'),
            ('A', 'Teaching Assistant'),
        )

    job = models.CharField(max_length=1, choices=TEACHER_OPTIONS)


####################################################################
###############          Dependent Models 2          ###############
####################################################################

class Course(models.Model):
    _id = models.CharField(primary_key=True, max_length=16)
    teachers = models.ManyToManyField(Teacher)

    name = models.CharField(max_length=32, null=True)

class Module_ed(models.Model):
    _id = models.CharField(primary_key=True, max_length=16)
    courses = models.ManyToManyField(Course)
    module_coordinator = models.ManyToManyField(Teacher)

    start = models.DateField(default=datetime.date(1,1,1))
    stop = models.DateField(default=datetime.date(1,1,1))

class Advisor(models.Model):
    _id = models.CharField(primary_key=True, max_length=16)
    studies = models.ManyToManyField(Study)

    name = models.CharField(max_length=32, null=True)
    mail = models.CharField(max_length=32, null=True)
    start = models.DateField(default=datetime.date(1,1,1))
    stop = models.DateField(default=datetime.date(1,1,1))

####################################################################
###############          Dependent Models 3          ###############
####################################################################

class Test(models.Model):
    course_id = models.ForeignKey(Course)

    name = models.CharField(max_length=32, null=True)
    TEST_TYPES = (             # Defaults to Exam
            ('E', 'Exam'),
            ('A', 'Assignment'),
            ('P', 'Project')
        )
    _type = models.CharField(max_length=1, choices=TEST_TYPES)
    time = models.DateField(default=datetime.date(1,1,1))


class Studying(models.Model):
    student_id = models.ForeignKey(Student)
    study = models.ForeignKey(Study)
    module_id = models.ForeignKey(Module_ed)
    role = models.CharField(max_length=32)

class Criterion(models.Model):
    study = models.ForeignKey(Study)
    module_id = models.ForeignKey(Module_ed)
    condition = models.CharField(max_length=32)
    role = models.CharField(max_length=32)


####################################################################
###############          Dependent Models 4          ###############
####################################################################

class Grade(models.Model):
    test_id = models.ForeignKey(Test)
    teacher_id = models.ForeignKey(Teacher)
    student_id = models.ForeignKey(Student)
    time = models.DateField(default=datetime.date(1,1,1))
    description = models.CharField(max_length=256, null=True)