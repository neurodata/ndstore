API Documentation Generation Guide
==================================

You need to install Epydoc_ >= 3.0 first to generate the TurboGears API
documentation from the source code.

You can install it via easy_install_::

    $ easy_install "epydoc>=3.0"

You also need to install Docutils 0.5 (Epydoc 3.0 has some problems with
newer Docutils releases) since this is used for parsing reStructuredText.

    $ easy_install "docutils==0.5"


Checking for missing doc strings
--------------------------------

To check which docs need to be written, use the following command in the
top directory of the TurboGears 1.5 branch::

    $ epydoc --check turbogears

The command will check that every module, class, method, and function has a
description; that every parameter has a description and a type; and that every
variable has a type. It will list those that don't meet these requirements.


Generating HTML docs
--------------------

Use this command in the top directory::

    $ ./doc/build_api_docs.sh

to generate the API documentation in the ``doc/api`` folder.

You can change the settings in the file ``doc.ini`` in the ``doc`` folder to
customize the output.


Writing docs
------------

.. note:: The TurboGears project uses reStructuredText_ format for doc strings.

It's a bit different from epydoc's default format. Check the documentation
about using reStructuredText with epydoc on the epydoc web site:

* http://epydoc.sourceforge.net/manual-docstring.html
* http://epydoc.sourceforge.net/manual-othermarkup.html
* http://epydoc.sourceforge.net/manual-fields.html


Debugging docs
--------------

If you get a formatting error and want to locate the position in the source
quickly, use the verbose mode of epydoc by supplying the ``-v`` option and
epydoc will print comprehensive debugging output.

The verbose mode is enabled in ``doc/doc.ini`` by default.


.. _epydoc: http://epydoc.sourceforge.net/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall
