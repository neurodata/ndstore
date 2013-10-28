"""TurboGears Front-to-Back Web Framework"""

__all__ = ['absolute_url', 'database', 'command', 'config',
    'controllers', 'expose', 'flash', 'error_handler',
    'exception_handler', 'mochikit', 'redirect',
    'scheduler', 'start_server', 'update_config',
    'url', 'validate', 'validators', 'view', 'widgets']

import warnings

import pkg_resources

from turbogears.release import (version as __version__, author as __author__,
    email as __email__, license as __license__, copyright as __copyright__)
from turbogears.config import update_config
from turbogears.controllers import (absolute_url, expose, flash, validate,
    redirect, error_handler, exception_handler, url)
from turbogears.paginate import paginate
from turbogears.widgets import mochikit, jsi18nwidget
from turbogears.startup import start_server
from turbogears import (config, controllers, view, database, validators,
    command, i18n, widgets, startup, scheduler)


# load global symbols for TG extensions (currently only used by tgfastdata)
extensions = pkg_resources.iter_entry_points('turbogears.extensions')
for entrypoint in extensions:
    try:
        extension = entrypoint.load()
        if hasattr(extension, 'tgsymbols'):
            globals().update(extension.tgsymbols())
    except Exception, exception:
        warnings.warn("Could not load extension %s from %s: %s"
            % (entrypoint, entrypoint.dist, exception), stacklevel=2)

i18n.install() # adds _ (gettext) to builtins namespace

