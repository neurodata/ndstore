# -*- coding: UTF-8 -*-

from sys import version_info as python_version
from setuptools import setup, find_packages

if python_version < (2, 4):
    raise SystemExit("TurboJson 1.3 requires Python 2.4 or later.")

setup(
    name = 'TurboJson',
    version = '1.3.2',
    description = 'Python template plugin that supports JSON',
    author = 'Elvelind Grandin et al',
    author_email = 'elvelind+turbogears@gmail.com',
    maintainer = 'TurboGears project',
    maintainer_email = 'turbogears@googlegroups.com',
    url = 'http://docs.turbogears.org/TurboJson',
    download_url = 'http://pypi.python.org/pypi/TurboJson',
    license = 'MIT',
    keywords = [
        'python.templating.engines',
        'turbogears'
    ],
    install_requires = [
        'PEAK-Rules >= 0.5a1.dev-r2600',
        # simplejson is actually available as json in the standard library
        # since Python 2.6, but the externally maintained package is newer
        # and can be substantially faster, so we always require it here
        'simplejson >= 1.9.1'
    ],
    tests_require = [
        'SQLAlchemy',
        'SQLObject'
    ],
    zip_safe = True,
    packages = find_packages(),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: TurboGears',
        'Environment :: Web Environment :: Buffet',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points = """\
    [python.templating.engines]
    json = turbojson.jsonsupport:JsonSupport
    """,
    test_suite = 'nose.collector'
)
