from django.db import models

class Module(models.Model):
        module_name = models.CharField(max_length=200)

