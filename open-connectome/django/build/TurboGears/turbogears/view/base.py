"""Template processing for TurboGears view layer.

The template engines are configured and loaded here and this module provides
the generic template rendering function "render", which selects the template
engine to use and the appropriate output format, headers and encoding based
on the given arguments and the application configuration.

Also defines the functions and variables that will be available in the
template scope and provides a hook for adding additional template variables.

"""

import sys
import re
import logging

from itertools import chain, imap
from itertools import cycle as icycle
from urllib import quote_plus

import pkg_resources

import cherrypy
try:
    import genshi
except ImportError:
    genshi = None
try:
    import kid
except ImportError:
    kid = None

import turbogears
from turbogears import identity, config

# the gettext imported here can be whatever function returned
# by the i18n module depending on the user's configuration
# all the functions will implement the same interface so we don't care
from turbogears.i18n import get_locale, gettext

from turbogears.util import (Bunch, adapt_call, get_template_encoding_default,
    get_mime_type_for_format, mime_type_has_charset)

try:
    from turbogears.i18n.kidutils import i18n_filter as kid_i18n_filter
except ImportError:
    kid_i18n_filter = None

try:
    from genshisupport import TGGenshiTemplatePlugin
except ImportError:
    TGGenshiTemplatePlugin = genshi_i18n_filter = None
else:
    try:
        from genshi.filters import Translator
    except ImportError:
        genshi_i18n_filter = None
    else:
        genshi_i18n_filter = Translator(gettext)

log = logging.getLogger('turbogears.view')

baseTemplates = []
variable_providers = []
root_variable_providers = []
engines = dict()


def _choose_engine(template):
    """Return template engine for given template name.

    Parses template name from the expose 'template' argument. If the @expose
    decorator did not contain a template argument, we fetch the default engine
    info from the configuration file.

    @param template: a template string as seen in the expose decorator.
        This can be something like 'kid:myproj.templates.welcome' or just
        'myproj.templates.welcome'.
        If a colon is found, then we try to get the engine name from the
        template string. Else we try to search it from the default engine in
        the configuration file via the `tg.defaultview` setting.
        The template name may also be just the name of the template engine,
        as in @expose('json').
    @type template: basestring or None

    """
    if isinstance(template, basestring):
        # if a template arg was given we try to find the engine declaration
        # in it by
        colon = template.find(':')
        if colon > -1:
            enginename = template[:colon]
            template = template[colon+1:]

        else:
            engine = engines.get(template, None)
            if engine:
                return engine, None, template
            enginename = config.get('tg.defaultview', 'genshi')

    else:
        enginename = config.get('tg.defaultview', 'genshi')

    engine = engines.get(enginename, None)

    if not engine:
        raise KeyError(
            "Template engine %s is not installed" % enginename)

    return engine, template, enginename


def render(info, template=None, format=None, headers=None, fragment=False,
           **options):
    """Renders data in the desired format.

    @param info: the data itself
    @type info: dict

    @param template: name of the template to use
    @type template: string

    @param format: 'html', 'xml', 'text' or 'json'
    @type format: string

    @param headers: for response headers, primarily the content type
    @type headers: dict

    @param fragment: passed through to tell the template if only a
                     fragment of a page is desired. This is a way to allow
                     xml template engines to generate non valid html/xml
                     because you warn them to not bother about it.
    @type fragment: bool

    All additional keyword arguments are passed as keyword args to the render
    method of the template engine.

    """
    environ = getattr(cherrypy.request, 'wsgi_environ', {})
    if environ.get('paste.testing', False):
        cherrypy.request.wsgi_environ['paste.testing_variables']['raw'] = info

    template = format == 'json' and 'json' or info.pop(
        'tg_template', template)

    if 'tg_flash' not in info:
        if config.get('tg.empty_flash', True):
            info['tg_flash'] = None

    engine, template, engine_name = _choose_engine(template)

    if format:
        if format == 'plain':
            if engine_name == 'genshi':
                format = 'text'

        elif format == 'text':
            if engine_name == 'kid':
                format = 'plain'

    else:
        format = engine_name == 'json' and 'json' or config.get(
            '%s.outputformat' % engine_name,
            config.get('%s.default_format' % engine_name, 'html'))

    if isinstance(headers, dict):
        # Determine the proper content type and charset for the response.
        # We simply derive the content type from the format here
        # and use the charset specified in the configuration setting.
        # This could be improved by also examining the engine and the output.
        content_type = headers.get('Content-Type')
        if not content_type:
            if format:
                content_format = format
                if isinstance(content_format, (tuple, list)):
                    content_format = content_format[0]

                if isinstance(content_format, str):
                    content_format = content_format.split(
                        )[0].split('-' , 1)[0].lower()

                else:
                    content_format = 'html'

            else:
                content_format = 'html'

            content_type = get_mime_type_for_format(content_format)

        if mime_type_has_charset(
                content_type) and '; charset=' not in content_type:
            charset = options.get('encoding',
                get_template_encoding_default(engine_name))

            if charset:
                content_type += '; charset=' + charset

        headers['Content-Type'] = content_type

    cherrypy.request.tg_template_engine_names = [engine_name]

    args, kw = adapt_call(engine.render, args=[], kw=dict(
        info=info, format=format, fragment=fragment, template=template,
        **options), start=1)

    return engine.render(**kw)


def transform(info, template):
    """Create ElementTree representation of the output."""
    engine, template, enginename = _choose_engine(template)
    return engine.transform(info, template)


def loadBaseTemplates():
    """Load base templates for use by other templates.

    By listing templates in turbogears.view.baseTemplates,
    these templates will automatically be loaded so that
    the "import" statement in a template will work.

    """
    log.debug("Loading base templates")
    for template in baseTemplates:
        engine, template, enginename = _choose_engine(template)
        if template in sys.modules:
            del sys.modules[template]
        engine.load_template(template)


class cycle:
    """Loops forever over an iterator.

    Wraps the itertools.cycle method, but provides a way to get the current
    value via the 'value' attribute.

    """
    value = None

    def __init__(self, iterable):
        self._cycle = icycle(iterable)

    def __str__(self):
        return self.value.__str__()

    def __repr__(self):
        return self.value.__repr__()

    def next(self):
        self.value = self._cycle.next()
        return self.value


def selector(expression):
    """If the expression is true, return the string 'selected'.

    Useful for HTML <option>s.

    """
    if expression:
        return 'selected'
    else:
        return None


def checker(expression):
    """If the expression is true, return the string "checked".

    This is useful for checkbox inputs.

    """
    if expression:
        return 'checked'
    else:
        return None


def ipeek(iterable):
    """Lets you look at the first item in an iterator.

    This is a good way to verify that the iterator actually contains something.
    This is useful for cases where you will choose not to display a list or
    table if there is no data present.

    """
    iterable = iter(iterable)
    try:
        item = iterable.next()
        return chain([item], iterable)
    except StopIteration:
        return None


class UserAgent:
    """Representation of the user's browser.

    Provides information about the type of browser, browser version, etc.
    This currently contains only the information needed for work thus far
    (msie, firefox, safari browser types, plus safari version info).

    """

    _re_safari = re.compile(r"Safari/(\d+)")

    def __init__(self, useragent=None):
        self.majorVersion = None
        self.minorVersion = None
        if not useragent:
            useragent = 'unknown'
        if useragent.find('MSIE') > -1:
            self.browser = 'msie'
        elif useragent.find('Firefox') > -1:
            self.browser = 'firefox'
        else:
            isSafari = self._re_safari.search(useragent)
            if isSafari:
                self.browser = 'safari'
                build = int(isSafari.group(1))
                # this comes from:
                # http://developer.apple.com/internet/safari/uamatrix.html
                if build >= 412:
                    self.majorVersion = '2'
                    self.minorVersion = '0'
                elif build >= 312:
                    self.majorVersion = '1'
                    self.minorVersion = '3'
                elif build >= 125:
                    self.majorVersion = '1'
                    self.minorVersion = '2'
                elif build >= 85:
                    self.majorVersion = '1'
                    self.minorVersion = '0'
            elif useragent == 'unknown':
                self.browser = 'unknown'
            else:
                self.browser = 'unknown: %s' % useragent


def genshi_et(element):
    """If this is an ElementTree element, convert it to a Genshi Markup stream.

    If this is a list, apply this function recursively and chain everything.

    """
    if hasattr(element, 'tag'):
        if not genshi:
            raise ImportError("Must convert ElementTree element to Genshi,"
                " but Genshi is not installed.")
        return genshi.input.ET(element)
    elif isinstance(element, list):
        return chain(*imap(genshi_et, element))
    else:
        return element


def kid_xml(stream):
    """If this is a Genshi Markup stream, convert it to a Kid ElementStream."""
    if hasattr(stream, 'render'):
        stream = stream.render('xml')
    if not kid:
        raise ImportError("Must convert Genshi markup stream to Kid,"
            " but Kid is not installed.")
    return kid.parser.XML(stream, fragment=True)


def stdvars():
    """Create a Bunch of variables that should be available in all templates.

    These variables are:

    checker
        the checker function
    config
        the cherrypy config get function
    cycle
        cycle through a set of values
    errors
        validation errors
    identity
        the current visitor's identity information
    inputs
        input values from a form
    ipeek
        the ipeek function
    locale
        the default locale
    quote_plus
        the urllib quote_plus function
    request
        the cherrypy request
    selector
        the selector function
    session
        the current cherrypy.session if tools.sessions.on is set in the
        app.cfg configuration file, otherwise session will be None
    tg_js
        the url path to the JavaScript libraries
    tg_static
        the url path to the TurboGears static files
    tg_toolbox
        the url path to the TurboGears toolbox files
    tg_version
        the version number of the running TurboGears instance
    url
        the turbogears.url function for creating flexible URLs
    useragent
        a UserAgent object with information about the browser

    Additionally, you can add a callable to turbogears.view.variable_providers
    that can add more variables to this list. The callable will be called with
    the vars Bunch after these standard variables have been set up.

    """
    try:
        useragent = cherrypy.request.headers['User-Agent']
        useragent = UserAgent(useragent)
    except Exception:
        useragent = UserAgent()

    if config.get('tools.sessions.on', None):
        session = cherrypy.session
    else:
        session = None

    webpath = turbogears.startup.webpath or ''
    tg_vars = Bunch(
        checker = checker,
        config = config.get,
        cycle = cycle,
        errors = getattr(cherrypy.request, 'validation_errors', {}),
        identity = identity.current,
        inputs = getattr(cherrypy.request, 'input_values', {}),
        ipeek = ipeek,
        locale = get_locale(),
        quote_plus = quote_plus,
        request = cherrypy.request,
        selector = selector,
        session = session,
        tg_js = webpath + '/tg_js',
        tg_static = webpath + '/tg_static',
        tg_toolbox = webpath + '/tg_toolbox',
        tg_version = turbogears.__version__,
        url = turbogears.url,
        useragent = useragent,
        widgets = webpath + '/tg_widgets',
    )
    for provider in variable_providers:
        provider(tg_vars)
    root_vars = dict()
    root_vars['_'] = gettext
    for provider in root_variable_providers:
        provider(root_vars)
    root_vars['tg'] = tg_vars
    root_vars['ET'] = genshi_et
    return root_vars


def _get_plugin_options(plugin_name, defaults=None):
    """Return all options from global config where the first part of the config
    setting name matches the start of plugin_name.

    Optionally, add default values from passed ``default`` dict where the first
    part of the key (i.e. everything leading up to the first dot) matches the
    start of ``plugin_name``. The defaults will be overwritten by the
    corresponding config settings, if present.

    """
    if defaults is not None:
        options = dict((k, v) for k, v in defaults.items()
            if plugin_name.startswith(k.split('.', 1)[0]))
    else:
        options = dict()
    for k, v in config.items():
        if plugin_name.startswith(k.split('.', 1)[0]):
            options[k] = v
    return options


def _get_genshi_loader_callback(template_filter):
    """Create a Genshi template loader callback for adding the given filter."""
    def genshi_loader_callback(template):
        template.filters.insert(0, template_filter)
    return genshi_loader_callback


def load_engines():
    """Load and initialize all templating engines.

    This is called during startup after the configuration has been loaded.
    You can call this earlier if you need the engines before startup;
    the engines will then be reloaded with the custom configuration later.

    """
    get = config.get

    engine_defaults = {
        'cheetah.importhooks': False,
        'cheetah.precompiled': False,
        'genshi.default_doctype':
            dict(html='html-strict', xhtml='xhtml-strict', xml=None),
        'genshi.default_encoding': 'utf-8',
        'genshi.lookup_errors': 'strict',
        'genshi.new_text_syntax': False,
        'json.assume_encoding': 'utf-8',
        'json.check_circular': True,
        'json.descent_bases': get('json.descent_bases',
            get('turbojson.descent_bases', True)),
        'json.encoding': 'utf-8',
        'json.ensure_ascii': False,
        'json.sort_keys': False,
        'kid.assume_encoding': 'utf-8',
        'kid.encoding': 'utf-8',
        'kid.precompiled': False,
        'kid.sitetemplate': get('kid.sitetemplate',
            get('tg.sitetemplate', 'turbogears.view.templates.sitetemplate')),
        'mako.directories': [''],
        'mako.output_encoding': 'utf-8'
    }

    # Check if the i18n filter is activated in configuration.
    # If so we'll need to add it to the Genshi or Kid template filters.
    if get('i18n.run_template_filter', False):
        i18n_filter = get('genshi.i18n_filter') or genshi_i18n_filter
        if i18n_filter:
            callback = _get_genshi_loader_callback(i18n_filter)
        i18n_filter = get('kid.i18n_filter') or kid_i18n_filter
        if i18n_filter:
            engine_defaults['kid.i18n_filter'] = i18n_filter
            engine_defaults['kid.i18n.run_template_filter'] = True

    for entrypoint in pkg_resources.iter_entry_points(
            'python.templating.engines'):
        engine = entrypoint.load()
        plugin_name = entrypoint.name
        engine_options = _get_plugin_options(plugin_name, engine_defaults)
        log.debug("Using options for template engine '%s': %r", plugin_name,
            engine_options)
        # Replace Genshi markup template engine with our own derived class
        # to support our extensions to the Buffet interface.
        # This is only a temporary measure. We should try to push our extension
        # upstream and then require a new Genshi version.
        if TGGenshiTemplatePlugin and plugin_name in (
                'genshi', 'genshi-markup'):
            engines[plugin_name] = TGGenshiTemplatePlugin(
                stdvars, engine_options)
        else:
            engines[plugin_name] = engine(stdvars, engine_options)
