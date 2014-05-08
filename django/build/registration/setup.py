#!/usr/bin/env python
from setuptools import setup, find_packages
from turbogears import finddata
import sys
import os

if sys.version_info < (2, 4):
    raise SystemExit("Python 2.4 or later is required")
    
execfile(os.path.join('registration', 'release.py'))

setup(name='registration',
    version=version,
    author=author,
    author_email=email,
    license=license,
    description=summary,
    url=home_page,
    platforms=['Any'],
    keywords = ['turbogears.quickstart.template'],
    classifiers = [
         'Development Status :: 4 - Beta',
         'Operating System :: OS Independent',
         'Programming Language :: Python',
         'Topic :: Software Development :: Libraries :: Python Modules',
         'Framework :: TurboGears',
         'License :: OSI Approved :: MIT License'
     ],
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    zip_safe=False,
    #package_data=finddata.find_package_data(),
    include_package_data=True,
    install_requires = ['TurboGears >= 1.0'],
    extras_require = {
        'turbomail' : ["TurboMail >= 2.0"]
    },
    entry_points="""
        [paste.paster_create_template]
            registration = registration:Registration
        """
    )