# -*- coding: UTF-8 -*-

"""\
Front-to-back rapid web development
===================================

TurboGears brings together four major pieces to create an easy to
install, easy to use web mega-framework. It covers everything from
front end (MochiKit JavaScript for the browser, Genshi / Kid / Mako /
Cheetah for templates in Python) to the controllers (CherryPy) to the
back end (SQLAlchemy or SQLObject).

The TurboGears project is focused on providing documentation and
integration with these tools without losing touch with the communities
that already exist around those tools.

TurboGears is easy to use for a wide range of web applications.

The latest development version is available in the `TurboGears
subversion repository`_.

Our `mailing list`_ is lively and helpful, don't hesitate to send your
questions there, we will try to help you find out a solution to your
problem.

.. _mailing list:
    http://groups.google.com/group/turbogears

.. _TurboGears subversion repository:
    http://svn.turbogears.org/trunk#egg=turbogears-dev
"""

version = "1.5.1"
description = "Front-to-back, open-source, rapid web development framework"
long_description = __doc__
author = "Kevin Dangoor"
email = "dangoor+turbogears@gmail.com"
maintainer = "TurboGears Release Team"
maintainer_email = "turbogears@googlegroups.com"
url = "http://www.turbogears.org/"
download_url = "http://www.turbogears.org/%s/downloads/%s/index" % (
    '.'.join(version.split('.', 2)[:2]), version)
dependency_links = [download_url]
copyright = "Copyright 2005 - 2011 Kevin Dangoor and contributors"
license = "MIT"
