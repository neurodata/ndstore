#!/usr/bin/env python
"""Distutils setup file"""
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup
PACKAGE_NAME = "PEAK-Rules"
PACKAGE_VERSION = "0.5a1"
PACKAGES = ['peak', 'peak.rules']

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
    description="Generic functions and business rules support systems",
    long_description = get_description(),
    install_requires=[
        'BytecodeAssembler>=0.6','DecoratorTools>=1.7dev-r2450',
        'AddOns>=0.6', 'Extremes>=1.1',
    ],
    author="Phillip J. Eby",
    author_email="peak@eby-sarna.com",
    license="ZPL 2.1",
    url="http://pypi.python.org/pypi/PEAK-Rules",
    download_url = "http://peak.telecommunity.com/snapshots/",
    test_suite = 'test_rules', tests_require='Importing',
    packages = PACKAGES,
    namespace_packages = ['peak'],
)
