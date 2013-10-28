#!/usr/bin/env python

import os
from setuptools import setup, find_packages

execfile(os.path.join('tgscheduler', 'release.py'))

packages = find_packages()
if os.path.isdir('locales'):
    packages.append('locales')

setup(
    name='TGScheduler',
    version=version,
    description=description,
    long_description=long_description,
    author=author,
    author_email=email,
    url=url,
    license=license,
    platforms=['any'],
    zip_safe=False,
    install_requires=[
        'python-dateutil >= 1.5, <2.0dev'
    ],
    packages=packages,
    #package_data=package_data,
    keywords=[
        'turbogears.widgets', 'tg2'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Widgets',
    ],
    test_suite = 'tgscheduler.tests',
)
