from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.db import models
from django.db.models import CASCADE
from django.urls import reverse
from django.utils import timezone


####################################################################
###############          Independent Models          ###############
####################################################################


class Module(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return '{}'.format(self.name)


####################################################################
###############          Dependent Models 1          ###############
####################################################################


class Person(models.Model):
    name = models.CharField(max_length=255)
    university_number = models.CharField(max_length=16, unique=True)
    email = models.EmailField(verbose_name='E-mail', null=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=CASCADE)

    @property
    def full_id(self):
        """Deprecated"""
        return self.university_number

    def __str__(self):
        return '{} ({})\t\t'.format(self.name, self.university_number)

    class Meta:
        ordering = ['university_number']


class Study(models.Model):
    abbreviation = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=255, unique=True)
    modules = models.ManyToManyField(Module, blank=True)
    advisers = models.ManyToManyField(Person, blank=True)

    def __str__(self):
        return self.name


####################################################################
###############          Dependent Models 2          ###############
####################################################################

def getyear():
    now = timezone.now()
    return now.year


class ModuleEdition(models.Model):
    module_code = models.CharField(max_length=32)
    year = models.IntegerField(default=getyear)
    module = models.ForeignKey(Module, on_delete=CASCADE)
    # Update BLOCKS in @property:get_blocks()
    BLOCKS = (
        ('1A', 'Block 1A'),
        ('1B', 'Block 1B'),
        ('2A', 'Block 2A'),
        ('2B', 'Block 2B'),
        ('3A', 'Block 3A'),
        ('3B', 'Block 3B'),
        ('JAAR', 'Block JAAR')
    )
    block = models.CharField(choices=BLOCKS, max_length=16)
    coordinators = models.ManyToManyField(Person, through='Coordinator', blank=True)

    @property
    def code(self):
        return '{}-{}-{}'.format(self.year, self.module_code, self.block)

    # Should be the same as BLOCKS
    @property
    def get_block(self):
        return {
            '1A': 'Block 1A',
            '1B': 'Block 1B',
            '2A': 'Block 2A',
            '2B': 'Block 2B',
            '3A': 'Block 3A',
            '3B': 'Block 3B',
            'JAAR': 'Block JAAR'
        }[self.block]

    def get_absolute_url(self):
        return reverse('module_management:module_edition_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '{} ({}-{})'.format(self.module.name, self.year, self.block)

    class Meta:
        ordering = ['-year', '-block', 'module']

    def validate_unique(self, exclude=None):
        super(ModuleEdition, self).validate_unique()
        if ModuleEdition.objects.filter(module=self.module, year=self.year, block=self.block).exists():
            raise ValidationError(
                {
                    NON_FIELD_ERRORS: [
                        'Module Edition is not unique',
                    ],
                }
            )


class ModulePart(models.Model):
    name = models.CharField(max_length=255)
    module_edition = models.ForeignKey(ModuleEdition, on_delete=CASCADE)
    teachers = models.ManyToManyField(Person, through='Teacher')

    @property
    def module_edition_code(self):
        return self.module_edition.code

    def get_absolute_url(self):
        return reverse('module_management:module_part_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '{} ({})'.format(self.name, self.module_edition_code)

    class Meta:
        ordering = ['module_edition', 'id']


class Coordinator(models.Model):
    person = models.ForeignKey(Person, on_delete=CASCADE)
    module_edition = models.ForeignKey(ModuleEdition, on_delete=CASCADE)
    is_assistant = models.BooleanField(default=False)

    class Meta:
        ordering = ['person']


class Teacher(models.Model):
    person = models.ForeignKey(Person, on_delete=CASCADE)
    module_part = models.ForeignKey(ModulePart, on_delete=CASCADE)
    # Update ROLES in @property:get_role()
    ROLES = (
        ('T', 'Teacher'),
        ('A', 'Teaching Assistant'),
    )
    role = models.CharField(max_length=1, choices=ROLES)

    # Should be the same as ROLES
    @property
    def get_role(self):
        return {
            'T': 'Teacher',
            'A': 'Teaching Assistant'
        }[self.role]

    class Meta:
        ordering = ['person']


####################################################################
###############          Dependent Models 3          ###############
####################################################################

class Test(models.Model):
    module_part = models.ForeignKey(ModulePart, on_delete=CASCADE)
    name = models.CharField(max_length=255, blank=True)
    # Update TEST_TYPES in @property:get_type()
    TEST_TYPES = (  # Defaults to Exam
        ('E', 'Exam'),
        ('A', 'Assignment'),
        ('P', 'Project')
    )
    type = models.CharField(max_length=1, choices=TEST_TYPES)
    maximum_grade = models.DecimalField(max_digits=4, decimal_places=1, default=10.0)
    minimum_grade = models.DecimalField(max_digits=4, decimal_places=1, default=1.0)
    released = models.BooleanField(default=False)

    def __str__(self):
        return '{} ({})'.format(self.name, self.type)

    # Should be the same as TEST_TYPES
    @property
    def get_type(self):
        return {
            'E': 'Exam',
            'A': 'Assignment',
            'P': 'Project'
        }[self.type]

    def get_absolute_url(self):
        return reverse('module_management:test_detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['module_part', '-type', 'id']


class Studying(models.Model):
    person = models.ForeignKey(Person, on_delete=CASCADE)
    # study = models.ForeignKey(Study)
    module_edition = models.ForeignKey(ModuleEdition, on_delete=CASCADE)
    role = models.CharField(max_length=32, blank=True)

    class Meta:
        unique_together = (('person', 'module_edition'),)

    def __str__(self):
        return '{} - {} ({})'.format(self.person, self.module_edition, self.role)  # , self.study)


class Criterion(models.Model):
    study = models.ForeignKey(Study, on_delete=CASCADE)
    module_edition = models.ForeignKey(ModuleEdition, on_delete=CASCADE)
    condition = models.CharField(max_length=32)
    role = models.CharField(max_length=32)

    def __str__(self):
        return self.condition


####################################################################
###############          Dependent Models 4          ###############
####################################################################

class Grade(models.Model):
    test = models.ForeignKey(Test, on_delete=CASCADE)
    teacher = models.ForeignKey(Person, related_name='Correcter', on_delete=CASCADE)
    student = models.ForeignKey(Person, related_name='Submitter', on_delete=CASCADE)
    time = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=255, blank=True)
    grade = models.DecimalField(max_digits=4, decimal_places=1, default=1.0)
    released = models.BooleanField(default=False)

    def __str__(self):
        return self.grade.__str__()
