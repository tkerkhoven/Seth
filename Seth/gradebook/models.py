from django.db import models

class Module(models.Model):
    module_name = models.CharField(max_length=50)
    # module_relevance_start = models.DateTimeField(auto_now_add=False)
    # module_relevance_stop = models.DateTimeField(auto_now_add=False)
    module_relevant = models.BooleanField(default=True)

class Module_ed(models.Model):
    module_code = models.CharField(primary_key=True, max_length=20)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    module_start = models.DateTimeField(auto_now_add=False)
    module_stop = models.DateTimeField(auto_now_add=False)
    

class Student(models.Model):
    student_id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=40)

class Study(models.Model):
    study_short = models.CharField(primary_key=True, max_length=10)
    study_long = models.CharField(max_length=50)

class Studying(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    module_code = models.ForeignKey(Module_ed, on_delete=models.CASCADE)
    study = models.ForeignKey(Study, on_delete=models.CASCADE)






