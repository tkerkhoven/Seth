from setuptools import setup

setup(
    name='Seth',
    version='1.0.0',
    package_dir={'': 'Seth'},
    url='https://mverkleij.nl/professional/seth',
    license='BSD 3-Clause License',
    author='Martijn Verkleij, Tim Kerkhoven, Kevin Hetterscheid, Gerwin Puttenstein and Jasper van Rooijen',
    author_email='seth@mverkleij.nl',
    description='Seth is a grade reporting system used in bachelor modules of Computer Science and BIT at the University of Twente.',

    requires=[
        'Django>=2',
        'psycopg2', # Postgres support
        'django-widget-tweaks',
        'pyrad',
        'future',
        'django-excel',
        'xlsxwriter', # Excel import and export
        'pyexcel-xls', # .xls file support
        'pyexcel-xlsx', # .xslx file support
                        # No .ods yet, but should not be hard to add
        'django-debug-toolbar',
        'django_select2', #Intelligent dropdowns
        'celery',
        'task',
        'django-celery',
        'anyjson',
    ]
)
