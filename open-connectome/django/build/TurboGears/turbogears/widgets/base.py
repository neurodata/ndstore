"""Base TurboGears widget implementation"""

__all__ = ['load_widgets', 'all_widgets', 'Widget', 'CompoundWidget',
    'WidgetsList', 'register_static_directory', 'static',
    'Resource', 'Link', 'CSSLink', 'JSLink',
    'Source', 'CSSSource', 'JSSource',
    'js_location', 'mochikit', 'jsi18nwidget',
    'WidgetDescription', 'set_with_self']

import os
import itertools
import warnings

import pkg_resources

from cherrypy import request
import tgmochikit

from turbogears import config, startup, view
from turbogears.util import (setlike, to_unicode, copy_if_mutable,
    get_package_name, request_available)
from turbogears.i18n.utils import get_locale
from turbogears.widgets.meta import MetaWidget, load_template


class Enum(set):
    """Enum used at js_locations.

    This is less strict than ``turbogears.utils.Enum`` and serves our
    purposes as well as allowing any object with ``retrieve_javascript``,
    ``retrieve_css``, and ``location`` attributes to provide resources to
    the template when scanned in ``turbogears.controllers._process_output``.

    Example:

        >>> locations = Enum('bodytop', 'bodybottom', head')
        >>> locations.head == locations.head
        True
        >>> locations.head == locations.bodybottom
        False
        >>> locations.head in locations
        True
        >>> locations.foo
        Traceback (most recent call last):
        ...
        AttributeError

    """

    def __init__(self, *args):
        set.__init__(self, args)

    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, ', '.join(map(repr, self)))


# Set up a counter for every declared widget in a WidgetsList instance,
# so their order is preserved.
counter = itertools.count()


def load_widgets():
    """Load all widgets provided by the widget entry point."""
    for widget_mod in pkg_resources.iter_entry_points('turbogears.widgets'):
        try:
            widget_mod.load()
        except Exception, e:
            raise ImportError('Error loading plugin "%s"\n%s: %s'
                % (widget_mod, e.__class__.__name__, e))

all_widgets = set()


#############################################################################
# Widgets base classes                                                      #
#############################################################################

class Widget(object):
    """A TurboGears Widget.

    '__init__' and 'update_params' are the only methods you might need to
    care extending.

    Attributes you should know about:

    name:        The name of the widget.
    template:    The Genshi or Kid template for the widget.
    engine_name: The name of the templating engine to be used for
                 rendering the template. You can also specify the engine
                 by adding a 'genshi:' or 'kid:' prefix to the template.
                 If the engine is not specified, and cannot be derived
                 from a xmlns:py attribute in the template source, then
                 the global default_engine ('genshi') will be used.
    default:     Default value for the widget.
    css:         List of CSSLinks and CSSSources for the widget. These
                 will be automatically pulled and inserted in the
                 page template that displays it.
    javascript:  List of JSLinks and JSSources for the widget. Same as css.
    is_named:    A property returning True if the widget has overridden its
                 default name.
    params:      All parameter names listed here will be treated as special
                 parameters. This list is updated by the metaclass and
                 always contains *all* params from the widget itself and
                 all its bases. Can be used as a quick reminder of all
                 the params your widget has at its disposal. They all
                 behave the same and have the same priorities regarding their
                 overridal. Read on...
    params_doc:  A dictionary containing 'params' names as keys and their
                 docstring as value. For documentation at the widget browser.

    All initialization parameters listed at the class attribute "params" can be
    defined as class attributes, overridden at __init__ or at display time.
    They will be treated as special params for the widget, which means:

    1) You can fix default values for them when subclassing Widget.

    2) If passed as **params to the constructor, the will be bound automatically
       to the widget instance, taking preference over any class attributes
       previously defined. Mutable attributes (dicts and lists) defined as class
       attributes are safe to modify as care is taken to copy them so the class
       attribute remains unchanged.

    3) They can be further overriden by passing them as keyword arguments to the
       display() method. This will only affect that display() method call in a
       thread-safe way.

    4) A callable can be passed and it will be called automatically when sending
       variables to the template. This can be handy to pick up parameters which
       change in every request or affect many widgets simultaneously.

    """

    __metaclass__ = MetaWidget

    name = "widget"
    template = None
    engine_name = None
    default = None
    css = []
    javascript = []
    params = []
    params_doc = {}

    def __init__(self, name=None, template=None, engine_name=None,
            default=None, **params):
        """Widget initialization.

        All initialization has to take place in this method.
        It's not thread-safe to mutate widget's attributes outside this method
        or anytime after widget's first display.

        *Must* call super(MyWidget, self).__init__(*args, **kw) cooperatively,
        unless, of course, you know what you're doing. Preferably this should
        be done before any actual work is done in the method.

        Parameters:

        name:        The widget's name. In input widgets, this will also be the
                     name of the variable that the form will send to the
                     controller. This is the only param that is safe to pass as a
                     positional argument to __init__.
        template:    The template that the widget should use to display itself.
                     Currently only Genshi and Kid templates are supported. You
                     can both initialize with a template string or with the path
                     to a file-base template: 'myapp.templates.widget_tmpl'
        engine_name: The engine to be used for rendering the template, if not
                     specified in the template already.
        default:     Default value to display when no value is passed at display
                     time.
        **params:    Keyword arguments specific to your widget or to any of its
                     bases. If listed at class attribute 'params' the will be
                     bound automatically to the widget instance.

        Note: Do not confuse these parameters with parameters listed at
        "params". Some widgets accept parameters at the constructor which are
        not listed params, these parameter won't be passed to the template, be
        automatically called, etc.

        """
        self._declaration_counter = counter.next()

        if name:
            self.name = name
        if engine_name and engine_name != self.engine_name:
            if self.template and not template:
                # load the template again with a different engine
                template = self.template
            self.engine_name = engine_name
        if template:
            self.template_c, self.template, self.engine_name = load_template(
                template, self.engine_name)
        if default is not None:
            self.default = default

        # logic for managing the params attribute
        for param in self.__class__.params:
            if param in params:
                # make sure we don't keep references to mutables
                setattr(self, param, copy_if_mutable(params.pop(param)))
            else:
                # make sure we don't alter mutable class attributes
                value, mutable = copy_if_mutable(
                    getattr(self.__class__, param), True)
                if mutable:
                    # re-set it only if mutable
                    setattr(self, param, value)

        for unused in params.iterkeys():
            warnings.warn('keyword argument "%s" is unused at %r instance' % (
                unused, self.__class__.__name__))

    def adjust_value(self, value, **params):
        """Adjust the value sent to the template on display."""
        return value

    def update_params(self, params):
        """Update the template parameters.

        This method will have the last chance to update the variables sent to
        the template for the specific request. All parameters listed at class
        attribute 'params' will be available at the 'params' dict this method
        receives.

        *Must* call super(MyWidget, self).update_params(params) cooperatively,
        unless, of course, your know what you're doing. Preferably this should
        be done before any actual work is done in the method.

        """
        pass

    # The following methods are needed to be a well behaved widget, however,
    # there is rarely the need to override or extend them if inheriting
    # directly or indirectly from Widget.

    def __call__(self, *args, **params):
        """Delegate to display. Used as an alias to avoid tiresome typing."""
        return self.display(*args, **params)

    def _prepare_params(self, value, params):
        """Prepare the widget params for rendering the template."""
        for param in self.__class__.params:
            if param in params:
                param_value = params[param]
                if callable(param_value):
                    param_value = param_value()
            else:
                # if the param hasn't been overridden (passed as a keyword
                # argument inside **params) put the corresponding instance
                # value inside params.
                param_value = getattr(self, param, None)
            # make sure we don't pass a reference to mutables
            params[param] = copy_if_mutable(param_value)
        if not params.get('name'):
            params['name'] = self.name
        if value is None:
            value = self.default
            if callable(value):
                value = value()
        params['value'] = to_unicode(self.adjust_value(value, **params))
        self.update_params(params)

    def display(self, value=None, **params):
        """Display the widget in a Genshi or Kid template.

        Returns a Genshi Markup stream or an ElementTree node instance,
        depending on the template in which the widget shall be displayed.
        If you need serialized output in a string, call 'render' instead.

        Probably you will not need to override or extend if inheriting from
        Widget.

        @params:

        value   : The value to display in the widget.
        **params: Extra parameters specific to the widget. All keyword params
                  supplied will pass through the update_params method which
                  will have a last chance to modify them before reaching the
                  template.

        """
        engine_name = self.engine_name
        if not getattr(self, 'template_c', False):
            warnings.warn(engine_name in view.engines
                and "Widget instance %r has no template defined" % self
                or "Trying to render a widget, but the %s templating engine"
                    " is not installed or not yet loaded." % engine_name)
            return None
        self._prepare_params(value, params)
        try:
            transform = view.engines[engine_name].transform
        except (KeyError, AttributeError):
            # this can happen if you render a widget before application startup
            # when view.load_engines() has not yet been called
            raise RuntimeError(
                "Trying to render a widget, but the %s templating engine"
                " is not installed or not yet loaded." % engine_name)

        # If the widget template is Kid, but the page template is Genshi,
        # we need to keep track of the nesting level, because Genshi cannot
        # display Kid's ElementTree elements directly.
        try:
            engine_names = request.tg_template_engine_names
        except AttributeError:
            request.tg_template_engine_names = engine_names = []
        engine_names.append(engine_name)
        try:
            output = transform(params, self.template_c)
            # convert output when switching between templating engines
            # and make sure parameters are evaluated on time in Genshi
            # (operating with streams doesn't work well with the path
            # acrobatics performed for properly handling nested form fields)
            if engine_names:
                adapter = {
                        'kid-genshi': view.kid_xml,
                        'genshi-kid': view.genshi_et,
                        'genshi-genshi': list
                    }.get('-'.join(engine_names[-2:]))
                if adapter:
                    output = adapter(output)
        finally:
            if engine_names:
                engine_names.pop()

        return output

    def render(self, value=None, format='html', **params):
        """Exactly the same as display() but return serialized output instead.

        Useful for debugging or to display the widget in a template other
        than Genshi or Kid, like Cheetah, Mako, Nevow Stan, ...

        """
        engine_name = self.engine_name
        if not getattr(self, 'template_c', False):
            warnings.warn(engine_name in view.engines
                and "Widget instance %r has no template defined" % self
                or "Trying to render a widget, but the %s templating engine"
                    " is not installed or not yet loaded." % engine_name)
            return None
        self._prepare_params(value, params)
        try:
            render = view.engines[engine_name].render
        except (KeyError, AttributeError):
            # this can happen if you render a widget before application startup
            # when view.load_engines() has not yet been called
            raise RuntimeError(
                "Trying to render a widget, but the %s templating engine"
                " is not installed or not yet loaded." % engine_name)

        try:
            engine_names = request.tg_template_engine_names
        except AttributeError:
            request.tg_template_engine_names = engine_names = []
        engine_names.append(engine_name)

        try:
            output = render(params,
                format=format, fragment=True, template=self.template_c)
        finally:
            if engine_names:
                engine_names.pop()

        return output

    def retrieve_javascript(self):
        """Return the needed JavaScript resources.

        Return a setlike instance containing all the JSLinks and JSSources
        the widget needs.

        """
        scripts = setlike()
        for script in self.javascript:
            scripts.add(script)
        return scripts

    def retrieve_css(self):
        """Return the needed CSS resources.

        Return a setlike instance with all the CSSLinks and CSSSources
        the widget needs.

        """
        css = setlike()
        for cssitem in self.css:
            css.add(cssitem)
        return css

    @property
    def is_named(self):
        """Return True if the widget has overridden its default name."""
        return self.name != "widget"

    def __setattr__(self, key, value):
        if self._locked:
            raise ValueError(
                "It is not threadsafe to modify widgets in a request")
        else:
            return super(Widget, self).__setattr__(key, value)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, ', '.join(
            ["%s=%r" % (var, getattr(self, var))
                for var in ['name'] + self.__class__.params]))


class CompoundWidget(Widget):
    """A widget that can contain other widgets.

    A compound widget is a widget that can group several widgets to make a
    complex widget. Child widget names must be listed at their widget's
    ``member_widgets`` attribute.

    """

    compound = True
    member_widgets = []

    def __init__(self, *args, **kw):
        # logic for managing the member_widgets attribute
        for member in self.__class__.member_widgets:
            if member in kw:
                setattr(self, member, kw.pop(member))
            elif not hasattr(self, member):
                setattr(self, member, None)
        super(CompoundWidget, self).__init__(*args, **kw)

    def iter_member_widgets(self):
        """Iterates over all the widget's children"""
        for member in self.__class__.member_widgets:
            attr = getattr(self, member, None)
            if isinstance(attr, list):
                for widget in attr:
                    yield widget
            elif attr is not None:
                yield attr

    def display(self, value=None, **params):
        params["member_widgets_params"] = params.copy()
        # logic for managing the member_widgets attribute
        for member in self.__class__.member_widgets:
            params[member] = getattr(self, member, None)
        return super(CompoundWidget, self).display(value, **params)

    def render(self, value=None, format='html', **params):
        params["member_widgets_params"] = params.copy()
        # logic for managing the member_widgets attribute
        for member in self.__class__.member_widgets:
            params[member] = getattr(self, member, None)
        return super(CompoundWidget, self).render(value, format, **params)

    def update_params(self, d):
        super(CompoundWidget, self).update_params(d)
        d['value_for'] = lambda f: self.value_for(f, d['value'])
        widgets_params = d['member_widgets_params']
        d['params_for'] = lambda f: self.params_for(f, **widgets_params)

    def value_for(self, item, value):
        """Get value for member widget.

        Pick up the value for a given member_widget 'item' from the
        value dict passed to this widget.

        """
        name = getattr(item, "name", item)
        if isinstance(value, dict):
            return value.get(name)
        else:
            return None

    def params_for(self, item, **params):
        """Get params for member widget.

        Pick up the params for the given member_widget 'item' from
        the params dict passed to this widget.

        """
        name = getattr(item, "name", item)
        item_params = {}
        for k, v in params.iteritems():
            if isinstance(v, dict):
                if name in v:
                    item_params[k] = v[name]
        return item_params

    def retrieve_javascript(self):
        """Get JavaScript for the member widgets.

        Retrieve the JavaScript for all the member widgets and
        get an ordered union of them.

        """
        scripts = setlike()
        for script in self.javascript:
            scripts.add(script)
        for widget in self.iter_member_widgets():
            for script in widget.retrieve_javascript():
                scripts.add(script)
        return scripts

    def retrieve_css(self):
        """Get CSS for the member widgets.

        Retrieve the CSS for all the member widgets and
        get an ordered union of them.

        """
        css = setlike()
        for cssitem in self.css:
            css.add(cssitem)
        for widget in self.iter_member_widgets():
            for cssitem in widget.retrieve_css():
                css.add(cssitem)
        return css


#############################################################################
# Declarative widgets support                                               #
#############################################################################

class MetaWidgetsList(type):
    """Metaclass for WidgetLists.

    Takes care that the resulting WidgetList has all widgets in the same order
    as they were declared.

    """

    def __new__(mcs, class_name, bases, class_dict):
        declared_widgets = []
        for base in bases:
            declared_widgets.extend(getattr(base, 'declared_widgets', []))
        for name, value in class_dict.items():
            if isinstance(value, Widget):
                if not value.is_named:
                    value.name = name
                declared_widgets.append(value)
                # we keep the widget accessible as attribute here,
                # i.e. we don't del class_dict[name] as we did before
        declared_widgets.sort(key=lambda w: w._declaration_counter)
        cls = type.__new__(mcs, class_name, bases, class_dict)
        cls.declared_widgets = declared_widgets
        return cls


class WidgetsList(list):
    """A widget list.

    That's really all. A plain old list that you can declare as a classs
    with widgets ordered as attributes. Syntactic sugar for an unsweet world.

    """

    __metaclass__ = MetaWidgetsList

    def __init__(self, *args):
        super(WidgetsList, self).__init__(self.declared_widgets)
        if args:
            if len(args) == 1:
                args = args[0]
                if isinstance(args, Widget):
                    args = [args]
            self.extend(args)
        if not self:
            warnings.warn("You have declared an empty WidgetsList")

    # Make WidgetsList instances usable as Widget containers in the dict
    # returned by controller methods, so that the JS/CSS resources of all
    # contained widgets get picked up by the templates:

    def retrieve_javascript(self):
        return itertools.chain(*(w.retrieve_javascript() for w in self
            if callable(getattr(w, 'retrieve_javascript', None))))

    def retrieve_css(self):
        return itertools.chain(*(w.retrieve_css() for w in self
            if callable(getattr(w, 'retrieve_css', None))))


#############################################################################
# CSS, JS and mochikit stuff                                                #
#############################################################################

def register_static_directory(modulename, directory):
    """Set up a static directory for JavaScript and CSS files.

    You can refer to this static directory in templates as
    ${tg.widgets}/modulename

    """
    directory = os.path.abspath(directory)
    config.update({'/tg_widgets/%s' % modulename: {
        'tools.staticdir.on' : True,
        'tools.staticdir.dir': directory
    }})

static = "turbogears.widgets"

register_static_directory(static,
    pkg_resources.resource_filename(__name__, 'static'))

register_static_directory('turbogears',
    pkg_resources.resource_filename('turbogears', 'static'))


def set_with_self(self):
    theset = setlike()
    theset.add(self)
    return theset


class Resource(Widget):
    """A resource for your widget.

    For example, this can be a link to an external JavaScript/CSS file
    or inline source to include at the template the widget is displayed.

    """
    order = 0
    params = ['order']
    params_doc = {
        'order': "JS and CSS are sorted in this 'order' at render time"
    }


class Link(Resource):
    """A widget resource that is a link."""

    def __init__(self, mod, *args, **kw):
        super(Link, self).__init__(*args, **kw)
        self.mod = mod

    def update_params(self, d):
        super(Link, self).update_params(d)
        d["link"] = "%s/tg_widgets/%s/%s" % (startup.webpath,
            self.mod, self.name)

    def __hash__(self):
        return hash(self.mod + self.name)

    def __eq__(self, other):
        return (self.mod == getattr(other, "mod", None)
            and self.name == getattr(other, "name", None))


class CSSLink(Link):
    """A CSS link."""

    template = """
    <link rel="stylesheet"
        type="text/css"
        href="$link"
        media="$media"
    />
    """
    params = ["media"]
    params_doc = {'media': 'Specify the media attribute for the CSS link tag'}
    media = "all"
    retrieve_css = set_with_self


js_location = Enum('head', 'bodytop', 'bodybottom')


class JSLink(Link):
    """A JavaScript link."""

    template = """
    <script type="text/javascript" src="$link"
        charset="$charset" defer="${defer and 'defer' or None}"/>
    """
    params = ["charset", "defer"]
    params_doc = {
        'charset': 'The character encoding of the linked script',
        'defer': 'If true, browser may defer execution of the script'
    }
    charset = None
    defer = False
    location = js_location.head

    def __init__(self, *args, **kw):
        location = kw.pop('location', None)
        super(JSLink, self).__init__(*args, **kw)
        if location:
            if location not in js_location:
                raise ValueError(
                    "JSLink location should be in %s" % js_location)
            self.location = location

    retrieve_javascript = set_with_self


class TGMochiKit(JSLink):
    """This JSLink includes MochkKit by means of the tgMochiKit project.

    Depending on three config options, you can decide

    ``tg_mochikit.version`` -- ``"1.3.1"``
        Which version of MochiKit should be used.
    ``tg_mochikit.packed`` -- ``False``
        Whether to deliver the MochiKit JS code packed or unpacked.
    ``tg_mochikit.xhtml`` -- ``False``
        Whether to be XHTML-compliant or not when ``tg_mochikit.packed`` is
        ``False``, i.e. selects whether the ``turbogears.mochikit`` widget
        should include all of MochiKit's submodules as separate JavaScript
        resources or just the main ``MochiKit.js`` file.

    For more explanation of the options, see the tgMochiKit documentation at

        http://docs.turbogears.org/tgMochiKit

    """

    template = """<script xmlns:py="http://genshi.edgewall.org/"
    py:for="js in javascripts" py:replace="js.display()"
    />
    """

    def retrieve_javascript(self):
        tgmochikit.init(register_static_directory, config)
        if config.get('tg.mochikit_suppress', False):
            if 'turbogears.mochikit' in config.get('tg.include_widgets', []):
                warnings.warn("""\
tg.mochikit_suppress == True, but 'turbogears.mochikit' is to be included via
'tg.include_widgets'. This is a contradiction, and mochikit_suppress overrides
the inclusion to prevent subtle errors due to version mixing of MochiKit.""")
            return []
        javascripts = [JSLink('tgmochikit', path)
            for path in tgmochikit.get_paths()]
        return javascripts

    def update_params(self, d):
        super(TGMochiKit, self).update_params(d)
        d['javascripts'] = self.retrieve_javascript()

mochikit = TGMochiKit('tgmochikit')


class JSI18NWidget(Widget):
    """JavaScript i18n support widget.

    This is a widget that can be used to add support for
    internationalization of JavaScript texts.

    It will basically add an implementation of the
    _ function that then can be used to wrap text literals
    in javascript-code.

    Additionally, message-catalogs are looked up and included
    depending on the current locale.

    To include the widget, put

    tg.include_widgets = ['turbogears.jsi18nwidget']

    in your application configuration.

    """

    params = ['locale_catalog_providers']
    locale_catalog_providers = []

    def __init__(self, *args, **kwargs):
        super(JSI18NWidget, self).__init__(*args, **kwargs)
        self._initialized = False

    def register_package_provider(self,
            package=None, directory=None, domain=None):

        parent = self

        class PackageProvider(object):
            def __init__(self):
                self._initialized = False

            def __call__(self, locale):
                if not self._initialized:
                    # the leading underscore is to prevent shadowing of the
                    # register_package_provider-arguments
                    if package is None:
                        _package = get_package_name()
                    else:
                        _package = package
                    if directory is None:
                        _directory = "static/javascript"
                    else:
                        _directory = directory
                    if domain is None:
                        _domain = config.get('i18n.domain', 'messages')
                    else:
                        _domain = domain
                    js_dir = pkg_resources.resource_filename(
                        _package, _directory)
                    register_static_directory(_package, js_dir)
                    self._package_name = _package
                    self._domain = _domain
                    self._initialized = True
                js = []
                for loc in locale, locale[:2]:
                    link = JSLink(
                        self._package_name, "%s-%s.js" % (self._domain, loc))
                    if parent.linked_file_exists(link):
                        js.append(link)
                        break
                return js

        self.locale_catalog_providers.append(PackageProvider())

    def retrieve_javascript(self):
        if not self._initialized:
            if not config.get('i18n.suppress_default_package_provider', False):
                self.register_package_provider()
            self._initialized = True
        js = super(JSI18NWidget, self).retrieve_javascript()
        js.add(JSLink('turbogears', 'js/i18n_base.js'))
        locale = get_locale()
        for pp in self.locale_catalog_providers:
            js.extend(pp(locale))
        return js

    def linked_file_exists(self, widget):
        widget_path = config.app.get('/tg_widgets/%s' % widget.mod)
        if widget_path:
            static_dir = widget_path.get('tools.staticdir.dir')
            if static_dir:
                return os.path.exists(os.path.join(static_dir, widget.name))
        return False

jsi18nwidget = JSI18NWidget()


class Source(Resource):

    params = ["src"]

    def __init__(self, src, *args, **kw):
        super(Source, self).__init__(*args, **kw)
        self.src = src

    def __hash__(self):
        return hash(self.src)

    def __eq__(self, other):
        return self.src == getattr(other, "src", None)


class CSSSource(Source):
    """A CSS source snippet."""

    template = """
    <style type="text/css" media="$media">$src</style>
    """
    params = ["media"]
    params_doc = {'src': 'The CSS source for the link',
                  'media' : 'Specify the media the css source link is for'}
    media = "all"
    retrieve_css = set_with_self


class JSSource(Source):
    """A JavaScript source snippet."""

    template = """
    <script type="text/javascript"
        defer="${defer and 'defer' or None}">$src</script>
    """
    params = ["defer"]
    params_doc = {'defer': 'If true, browser may defer execution of the script'}
    defer = False
    location = js_location.head

    def __init__(self, src, location=None, **kw):
        if location:
            if location not in js_location:
                raise ValueError(
                    "JSSource location should be in %s" % js_location)
            self.location = location
        super(JSSource, self).__init__(src, **kw)

    retrieve_javascript = set_with_self


#############################################################################
# Classes for supporting the toolbox widget browser                         #
#############################################################################

class MetaDescription(MetaWidget):
    """Metaclass for widget descriptions.

    Makes sure the widget browser knows about all of them as soon as they
    come into existence.

    """

    def __init__(mcs, name, bases, dct):
        super(MetaDescription, mcs).__init__(name, bases, dct)
        register = dct.get('register', True)
        if name != 'WidgetDescription' and register:
            all_widgets.add(mcs)


class WidgetDescription(CompoundWidget):
    """A description for a Widget.

    Makes the 'for_widget' widget appear in the browser. It's a nice way to
    show off to your friends your coolest new widgets and to have a testing
    platform while developing them.

    """

    __metaclass__ = MetaDescription

    template = """
    <div xmlns:py="http://genshi.edgewall.org/"
        py:content="for_widget.display()"/>
    """
    for_widget = None
    member_widgets = ["for_widget"]
    show_separately = False

    @property
    def name(self):
        return self.for_widget_class.__name__

    @property
    def for_widget_class(self):
        return self.for_widget.__class__

    @property
    def description(self):
        return self.for_widget_class.__doc__

    @property
    def full_class_name(self):
        cls = self.for_widget_class
        return "%s.%s" % (cls.__module__, cls.__name__)

    @property
    def source(self):
        import inspect
        return inspect.getsource(self.__class__)

    def retrieve_css(self):
        return self.for_widget.retrieve_css()

    def retrieve_javascript(self):
        return self.for_widget.retrieve_javascript()


class CoreWD(WidgetDescription):

    register = False

    @property
    def full_class_name(self):
        cls = self.for_widget_class
        return "turbogears.widgets.%s" % (cls.__name__)


class RenderOnlyWD(WidgetDescription):

    register = False
    template = """
    <div>
        This widget will render like that:<br/><br/>
        <tt class="rendered">${for_widget.render(value)}</tt>
    </div>
    """

    def retrieve_javascript(self):
        return setlike()

    def retrieve_css(self):
        return setlike()


#############################################################################
# CSS and JS WidgetDescription's                                            #
#############################################################################

class CSSLinkDesc(CoreWD, RenderOnlyWD):

    name = "CSS Link"
    for_widget = CSSLink('turbogears', 'css/yourstyle.css')


class JSLinkDesc(CoreWD, RenderOnlyWD):

    name = "JS Link"
    for_widget = JSLink('turbogears', 'js/yourscript.js')


class CSSSourceDesc(CoreWD, RenderOnlyWD):

    name = "CSS Source"
    for_widget = CSSSource("body { font-size:12px; }")


class JSSourceDesc(CoreWD, RenderOnlyWD):

    name = "JS Source"
    for_widget = JSSource("document.title = 'Hello World';")

