from django.db import models

####################################################################
###############          Independent Models          ###############
####################################################################

class Module(models.Model):
    name = models.CharField(max_length=32)

class Student(models.Model):
    student_id = models.CharField(primary_key=True, max_length=16)

class Advisor(models.Model):
    advisor_id = models.CharField(primary_key=True, max_length=16)


####################################################################
###############          Dependent Models 1          ###############
####################################################################

class Study(models.Model):
    short_name = models.CharField(primary_key=True, max_length=10)
    modules = models.ManyToManyField(Module)

class Teacher(models.Model):
    teacher_id = models.CharField(primary_key=True, max_length=16)
    student_id = models.ForeignKey(Student)

####################################################################
###############          Dependent Models 2          ###############
####################################################################

class Course(models.Model):
    course_id = models.CharField(primary_key=True, max_length=16)
    teachers = models.ManyToManyField(Teacher)

class Module_ed(models.Model):
    module_ed_id = models.CharField(primary_key=True, max_length=16)
    courses = models.ManyToManyField(Course)

####################################################################
###############          Dependent Models 3          ###############
####################################################################

class Test(models.Model):
    course_id = models.ForeignKey(Course)

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