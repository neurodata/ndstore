tgMochiKit
==========

:Status: Official

.. contents::
    :depth: 2


Author:
    Diez B. Roggisch
Release information and download URL:
    http://pypi.python.org/pypi/tgMochiKit
SVN repository:
    http://svn.turbogears.org/projects/tgMochiKit


Overview
--------

This is a packaging of the MochiKit_ JavaScript library as a TurboGears widget.
MochiKit is authored by Bob Ippolito.


Usage
-----

There are two main ways to use tgMochiKit with TurboGears:

#. as a standalone widget
#. as a resource for another widget


Using tgMochiKit as a Stand-alone Widget
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is usually done by letting TurboGears include the tgMochiKit widget on
every page, so that other JavaScript code on the page can utilize the functions
of the MochiKit library. You do this by setting the following in your
application's main configuration_::

    tg.include_widgets = ['turbogears.mochikit']

.. note::
    Please note that the ``mochikit`` widget object lives in the ``turbogears``
    module, since when TurboGears initializes the ``widgets`` package, it
    selects the right MochiKit version depending on the application's
    configuration. See the `Configuration Reference`_ below for more
    information.


Using tgMochiKit as a Resource for Another Widget
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a JavaScript-enabled widget relies on the MochiKit library it should declare
the tgMochiKit widget as a resource by adding it to its ``javascript`` class
attribute.

Here is a small sample widget that uses the MochiKit ``Logging`` module::

    from turbogears import widgets, mochikit

    class LoggingPanelLink(widget.widget):
        template = """\
    <a href="#" onclick="MochiKit.Logging.logger.debuggingBookmarklet();"
        >open logging pane</a>
    """
        javascript = [mochikit]


Using tgMochiKit in TG 1.0
~~~~~~~~~~~~~~~~~~~~~~~~~~

TurboGears 1.0 ships with the released MochiKit version 1.3.1. But as this is 
pretty dated, the desire to use newer releases often arises.

To do that with tgMochiKit is simple:

#. Use ``tg.mochikit_suppress = True`` in your ``app.cfg`` to prevent the  
   inclusion of the shipped MK.

#. In e.g. ``<myproject>.__init__.py`` include the following snippet::

    ### tgMochiKit

    import tgmochikit
    from turbogears.widgets import register_static_directory, Widget, JSLink

    tgmochikit.init(register_static_directory, version="1.4", xhtml=True)

    class TGMochiKit(Widget):
        def retrieve_javascript(self):
            jss = [JSLink("tgmochikit", path)
                for path in tgmochikit.get_paths()]
            return jss

        mochikit = TGMochiKit()

    ### tgMochiKit

#. in your ``app.cfg``, put ``<myproject>.mochikit`` into the
   ``tg.include_widgets`` list.


Configuration Reference
-----------------------

``tg.include_widgets -- []``
    This option automatically includes the listed widgets in all pages on the
    site. See `Using tgMochiKit as a Stand-alone Widget`_ above
    on how to employ this for tgMochiKit.

``tg.mochikit_suppress -- False``
    Setting this to ``True`` will prevent the inclusion of the MochiKit version
    1.3.1, that comes shipped with TurboGears 1.0, in the (X)HTML template
    output. This allows to include your own custom mochikit versions. This
    option takes precedence if ``'turbogears.mochikit'`` is listed in the
    ``tg.include_widgets`` setting.

``tg_mochikit.version -- 1.3.1``
    This setting selects the version of the MochiKit library that the
    ``turbogears.mochikit`` widget will use. tgMochiKit currently ships
    with version 1.3.1, 1.4 and several snapshots of the 1.4 development version.

``tg_mochikit.packed -- False``
    Selects whether the ``turbogears.mochikit`` widget will use the packed
    version or the unpacked version of the MochiKit JavaScript library.

``tg_mochikit.xhtml -- False``
    Selects whether the ``turbogears.mochikit`` widget should include all of
    MochiKit's submodules as separate JavaScript resources or just the main
    ``MochiKit.js`` file.

``tg_mochikit.draganddrop -- False``
    Selects if the ``turbogears.mochikit`` widget should include the
    ``DragAndDrop.js`` file.

Version selection
-----------------

tgMochiKit ships with various versions of MochKit.

 - the stable 1.3.1 version, as used by the TurboGears 1.0.x series.
 - as of 10/21/2008, the released 1.4 version.
 - various snapshots of the 1.4 version from the subversion.
 - the ``trunk``, also a subversion snapshot, which reflects the
   version inside trunk at the time of the tgMochiKit release you are using.

You can get the shipped versions by doing :::

  >>> import tgmochikit
  >>> print tgmochikit.get_shipped_versions()


Chosing the right version
~~~~~~~~~~~~~~~~~~~~~~~~~


Now when using tgMochiKit, the problem of which version to chose arises. 

If you want 1.3.1, just configure that as version to chose.

If you want a specific version that is shipped, configure that. This is the
safe course of action for you application, because by this you ensure that
even if you install newer versions of tgMochiKit (which might happen due
to TurboGears upgrades), you will end up with code you verified that it works.

.. 
   If you feel confident that using the latest of MochiKit is ok for you, configure
   ``tg_mochikit.version`` to be ``1.4``. This will always pick the newest from the 
   pack.

The ``trunk``-version is something special. In the shipped tgMochiKit it will always
be equal to the latest 1.4 version.

However, if you want the latest from trunk, you can simply 

 - check out tgMochiKit. This will fetch the latest from trunk into the distribution
 - create your own tgMochiKit.egg, and use that for your application.

The version actually used by tgMochiKit based on your configuration is by the way
logged on the logger ``tgmochikit`` with level ``INFO`` with the text::

  Version chosen: <version>

Installation
------------

You can install the tgMochiKit widget package via easy_install_::

    [sudo] easy_install tgMochiKit

tgMochiKit will be installed automatically as a requirement when you install
TurboGears 1.1.x.

TurboGears 1.0.x comes with a widget for MochiKit version 1.3.1 included in the
main distribution, so you don't need to install tgMochiKit, unless you want to
use a newer version of MochiKit.


Requirements
~~~~~~~~~~~~

tgMochiKit relies on the TurboGears widget framework to be useful and is only
properly initialised when you use TurboGears 1.1.

To make it work with TurboGears 1.0, see `Using tgMochiKit in TG 1.0`_. 


References
----------

To find out more about TurboGears widgets go here:

    http://docs.turbogears.org/1.0/Widgets

For more information on how to create widget packages, visit:

    http://docs.turbogears.org/1.0/WidgetPackages

.. _mochikit: http://mochikit.com/
.. _configuration: http://docs.turbogears.org/1.0/Configuration
.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall

