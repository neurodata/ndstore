#!/usr/bin/env python
"""Distutils setup file"""

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

# Metadata
PACKAGE_NAME = "DecoratorTools"
PACKAGE_VERSION = "1.8"
PACKAGES = ['peak', 'peak.util']

def get_description():
    # Get our long description from the documentation
    f = file('README.txt')
    lines = []
    for line in f:
        if not line.strip():
            break     # skip to first blank line
    for line in f:
        if line.startswith('.. contents::'):
            break     # read to table of contents
        lines.append(line)
    f.close()
    return ''.join(lines)

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description="Class, function, and metaclass decorators -- even in Python 2.3"
                " (now with source debugging for generated code)!",
    long_description = get_description(),
    author="Phillip J. Eby",
    author_email="peak@eby-sarna.com",
    license="PSF or ZPL",
    url="http://cheeseshop.python.org/pypi/DecoratorTools",
    test_suite = 'test_decorators',
    packages = PACKAGES,
    namespace_packages = PACKAGES,
)

