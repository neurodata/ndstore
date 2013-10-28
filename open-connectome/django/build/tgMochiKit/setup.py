from setuptools import setup, find_packages

import os
execfile(os.path.join("tgmochikit", "release.py"))

setup(
    name="tgMochiKit",
    version=version,

    description=description,
    author=author,
    author_email=email,
    url=url,
    download_url=download_url,
    license=license,

    install_requires = [],
    scripts = [],
    zip_safe=False,
    packages=find_packages(),
    include_package_data = True,
    keywords = [
        'turbogears.widgets',
    ],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Widgets',
    ],
    entry_points = """
    [turbogears.widgets]
    tgmochikit = tgmochikit
    """,
    test_suite = 'nose.collector',
)
