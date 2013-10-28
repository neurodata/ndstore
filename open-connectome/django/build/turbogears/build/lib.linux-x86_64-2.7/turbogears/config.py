"""TurboGears configuration"""

__all__ = ['update_config', 'get', 'update']

import os, glob, re

import cherrypy
from cherrypy import request, config as cp_config, log as cp_log
from configobj import ConfigObj
import pkg_resources
import logging.handlers

# TurboGear's server-side config just points directly to CherryPy.
server = cp_config

# Possible section names for the server-side configuration:
server_sections = ('DEFAULT', 'global', 'server')

# The application config is used when mounting applications.
# Config values that are not server-wide should be put here.
app = dict()

# Possible section names for the logging configuration:
logging_sections = ('logging',)


class ConfigError(Exception):
    """TurboGears configuration error."""


def _get_formatters(formatters):
    """Helper function for getting formatters from the logging config."""
    for key, formatter in formatters.items():
        kw = {}
        fmt = formatter.get('format', None)
        if fmt:
            fmt = fmt.replace('*(', '%(')
            kw["fmt"] = fmt
        datefmt = formatter.get('datefmt', None)
        if datefmt:
            kw['datefmt'] = datefmt
        formatter = logging.Formatter(**kw)
        formatters[key] = formatter


def _get_handlers(handlers, formatters):
    """Helper function for getting the handler from the logging config."""
    for key, handler in handlers.items():
        try:
            cls = handler.get('class')
            args = handler.get('args', tuple())
            level = handler.get('level', None)
            try:
                cls = eval(cls, logging.__dict__)
            except NameError:
                try:
                    cls = eval(cls, logging.handlers.__dict__)
                except NameError, err:
                    raise ConfigError("Specified class in handler %s"
                        " is not a recognizable logger name" % key)
            try:
                handler_obj = cls(*eval(args, logging.__dict__))
            except IOError,err:
                raise ConfigError("Missing or wrong argument to %s"
                    " in handler %s -> %s " % (cls.__name__,key,err))
            except TypeError,err:
                raise ConfigError("Wrong format for arguments to %s"
                    " in handler %s -> %s" % (cls.__name__,key,err))
            if level:
                level = eval(level, logging.__dict__)
                handler_obj.setLevel(level)
        except KeyError:
            raise ConfigError("No class specified for logging handler %s"
                % key)
        formatter = handler.get('formatter', None)
        if formatter:
            try:
                formatter = formatters[formatter]
            except KeyError:
                raise ConfigError("Handler %s references unknown formatter %s"
                    % (key, formatter))
            handler_obj.setFormatter(formatter)
        handlers[key] = handler_obj


def _get_loggers(loggers, handlers):
    """Helper function for getting the loggers from the logging config."""
    for key, logger in loggers.items():
        qualname = logger.get('qualname', None)
        if qualname:
            log = logging.getLogger(qualname)
        else:
            log = logging.getLogger()

        level = logger.get('level', None)
        if level:
            level = eval(level, logging.__dict__)
        else:
            level = logging.NOTSET
        log.setLevel(level)

        propagate = logger.get('propagate', None)
        if propagate is not None:
            log.propagate = propagate

        cfghandlers = logger.get('handlers', None)
        if cfghandlers:
            if isinstance(cfghandlers, basestring):
                cfghandlers = [cfghandlers]
            for handler in cfghandlers:
                try:
                    handler = handlers[handler]
                except KeyError:
                    raise ConfigError("Logger %s references unknown handler %s"
                        % (key, handler))
                log.addHandler(handler)
        if qualname == 'cherrypy.error':
            cp_log.error_log = log
        elif qualname == 'cherrypy.access':
            cp_log.access_log = log


def configure_loggers(logcfg):
    """Configures the Python logging module.

    We are using options that are very similar to the ones listed in the
    Python documentation. This also removes the logging configuration from
    the configuration dictionary because CherryPy doesn't like it there.
    Here are some of the Python examples converted to the format used here:

    [logging]
    [[loggers]]
    [[[parser]]]
    [logger_parser]
    level="DEBUG"
    handlers="hand01"
    propagate=1
    qualname="compiler.parser"

    [[handlers]]
    [[[hand01]]]
    class="StreamHandler"
    level="NOTSET"
    formatter="form01"
    args="(sys.stdout,)"

    [[formatters]]
    [[[form01]]]
    format="F1 *(asctime)s *(levelname)s *(message)s"
    datefmt=

    One notable format difference is that *() is used in the formatter
    instead of %() because %() is already used for config file interpolation.

    """
    formatters = logcfg.get('formatters', {})
    _get_formatters(formatters)

    handlers = logcfg.get('handlers', {})
    _get_handlers(handlers, formatters)

    loggers = logcfg.get('loggers', {})
    _get_loggers(loggers, handlers)


def config_defaults():
    """Return a dict with default global config settings."""
    return dict(
        current_dir_uri=os.path.abspath(os.getcwd())
    )


def config_obj(configfile=None, modulename=None):
    """Read configuration from given config file and/or module.

    See the docstring of the 'update_config' function for parameter description.

    Returns a config.ConfigObj object.

    """
    defaults = config_defaults()

    if modulename:
        firstdot = modulename.find('.')
        if firstdot < 0:
            raise ConfigError('Config file package not specified')
        lastdot = modulename.rfind('.')
        top_level_package = modulename[:firstdot]
        packagename = modulename[:lastdot]
        modname = modulename[lastdot+1:]
        modfile = pkg_resources.resource_filename(packagename, modname + '.cfg')
        if not os.path.exists(modfile):
            modfile = pkg_resources.resource_filename(packagename, modname)
        if os.path.isdir(modfile):
            configfiles = glob.glob(os.path.join(modfile, '*.cfg'))
        else:
            configfiles = [modfile]
        configdata = ConfigObj(unrepr=True)
        top_level_dir = os.path.normpath(pkg_resources.resource_filename(
            top_level_package, ''))
        package_dir = os.path.normpath(pkg_resources.resource_filename(
            packagename, ''))
        defaults.update(dict(top_level_dir=top_level_dir,
            package_dir=package_dir))
        configdata.merge(dict(DEFAULT=defaults))
        for file in configfiles:
            configdata2 = ConfigObj(file, unrepr=True)
            configdata2.merge(dict(DEFAULT=defaults))
            configdata.merge(configdata2)

    if configfile:
        if modulename:
            configdata2 = ConfigObj(configfile, unrepr=True)
            configdata2.merge(dict(DEFAULT=defaults))
            configdata.merge(configdata2)
        else:
            configdata = ConfigObj(configfile, unrepr=True)
    return configdata


def update_config(configfile=None, modulename=None):
    """Update the system configuration from given config file and/or module.

    'configfile' is a ConfigObj (INI-style) config file, 'modulename' a module
    path in dotted notation. The function looks for files with a ".cfg"
    extension if the given module name refers to a package directory or a file
    with the base name of the right-most part of the module path and a ".cfg"
    extension added.

    If both 'configfile' and 'modulname' are specified, the module is read
    first, followed by the config file. This means that the config file's
    options override the options in the module file.

    """
    configdict = config_obj(configfile, modulename).dict()
    update(configdict)


_obsolete_names = set("""autoreload before_main filters
baseurl_filter cache_filter decoding_filter encoding_filter gzip_filter
log_debug_info_filter nsgmls_filter response_headers_filter
session_authenticate_filter session_auth session_filter
static_filter tidy_filter virtual_host_filter wsgiappfilter xmlrpc_filter
log_access_file log_file log_to_screen show_tracebacks throw_errors
""".split())

_tools_names = ('toscawidgets', 'visit')

def _check_name(name):
    """Check name and return translated name where applicable.

    In order to keep the config settings simple and compatible among
    versions, we hide the fact that some features are currently implemented
    as CherryPy tools and just silently add settings with the tools prefix.

    """
    basename = name.split('.', 1)[0]
    if basename in _tools_names:
        return 'tools.' + name
    elif basename in _obsolete_names:
        raise KeyError("The config setting %s is obsolete."
            " Check the CherryPy 3 docs for the new setting." % name)


def update(configvalues):
    """Update the configuration with values from a dictionary.

    The values are sent to the appropriate config system
    (server, app, or logging) automatically.

    """
    global server, app

    # Send key values for applications to app, logging to logging, and
    # the rest to server. app keys are identified by their leading slash.
    for key, value in configvalues.iteritems():
        if not isinstance(key, basestring):
            raise ValueError("Key error in config update: %r" % key)
        if key.startswith('/'):
            if key in app:
                app[key].update(value)
            else:
                app[key] = value
            mounted_app = cherrypy.tree.apps.get('')
            if mounted_app:
                mounted_app.merge({key:value})
        elif key in logging_sections:
            configure_loggers(value)
        elif key in server_sections and isinstance(value, dict):
            server.update(value)
            for key in value:
                add_key = _check_name(key)
                if add_key:
                    server[add_key] = value[key]
        else:
            server[key] = value
            add_key = _check_name(key)
            if add_key:
                server[add_key] = value


def get(key, *args):
    """Get a config setting.

    Uses request.config if available, otherwise defaults back to the
    server's config settings.

    """
    config = getattr(request, 'stage', None) and request.config or server
    value = config.get(key, *args)
    if value and key == 'sqlobject.dburi' and os.name == 'nt':
        value = re.sub('///([A-Za-z]):', r'///\1|', value)
    return value


def copy():
    """Copy server config settings."""
    return server.copy()


def items():
    """A dict.items() equivalent for config values.

    Returns request specific information if available, otherwise falls back
    to server config.

    """
    if getattr(request, 'stage', None):
        return request.config.items()
    else:
        return server.items()
