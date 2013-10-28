#!/usr/bin/env python
"""Distutils setup file, used to install or test 'setuptools'"""

import textwrap
import sys

try:
    import setuptools
except ImportError:
    sys.stderr.write("Distribute 0.7 may only upgrade an existing "
        "Distribute 0.6 installation")
    raise SystemExit(1)

long_description = textwrap.dedent("""
    Distribute - legacy package

    This package is a simple compatibility layer that installs Setuptools 0.7+.
    """).lstrip()

setup_params = dict(
    name="distribute",
    version='0.7.3',
    description="distribute legacy wrapper",
    author="The fellowship of the packaging",
    author_email="distutils-sig@python.org",
    license="PSF or ZPL",
    long_description=long_description,
    keywords="CPAN PyPI distutils eggs package management",
    url="http://packages.python.org/distribute",
    zip_safe=True,

    classifiers=textwrap.dedent("""
        Development Status :: 5 - Production/Stable
        Intended Audience :: Developers
        License :: OSI Approved :: Python Software Foundation License
        License :: OSI Approved :: Zope Public License
        Operating System :: OS Independent
        Programming Language :: Python :: 2.4
        Programming Language :: Python :: 2.5
        Programming Language :: Python :: 2.6
        Programming Language :: Python :: 2.7
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3.1
        Programming Language :: Python :: 3.2
        Programming Language :: Python :: 3.3
        Topic :: Software Development :: Libraries :: Python Modules
        Topic :: System :: Archiving :: Packaging
        Topic :: System :: Systems Administration
        Topic :: Utilities
        """).strip().splitlines(),

    install_requires=[
        'setuptools>=0.7',
    ],
)

if __name__ == '__main__':
    setuptools.setup(**setup_params)
