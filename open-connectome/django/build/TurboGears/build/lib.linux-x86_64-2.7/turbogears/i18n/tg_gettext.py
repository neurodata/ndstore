import os
import sys
import logging

from gettext import translation

from turbojson.jsonify import jsonify

from turbogears import config
from turbogears.util import get_package_name, request_available
from turbogears.i18n.utils import get_locale

try:
    from turbogears.i18n.sogettext import so_gettext
except ImportError:
    so_gettext = None
try:
    from turbogears.i18n.sagettext import sa_gettext
except ImportError:
    sa_gettext = None

log = logging.getLogger('turbogears.i18n')


_catalogs = {}


def get_locale_dir():
    localedir = config.get('i18n.locale_dir')

    if not localedir:
        package = get_package_name()
        if package:
            localedir = os.path.join(os.path.dirname(
                sys.modules[package].__path__[0]), 'locales')

    return localedir


def is_locale_supported(locale, domain=None):
    """Check if [domain].mo file exists for this language."""
    if not domain:
        domain = config.get('i18n.domain', 'messages')

    localedir = get_locale_dir()
    return localedir and os.path.exists(os.path.join(
        localedir, locale, 'LC_MESSAGES', '%s.mo' % domain))


def get_catalog(locale, domain=None):
    """Return translations for given locale."""
    if not domain:
        domain = config.get('i18n.domain', 'messages')

    catalog = _catalogs.setdefault(domain, {})

    try:
        messages = catalog[locale]
    except KeyError:
        localedir = get_locale_dir()
        languages = [locale]
        if len(locale) > 2:
            languages.append(locale[:2])
        try:
            messages = translation(domain=domain,
                localedir=localedir, languages=languages)
        except (KeyError, IOError):
            messages = None
        catalog[locale] = messages

    return messages


def plain_gettext(key, locale=None, domain=None):
    """Get the gettext value for key.

    Added to builtins as '_'. Returns Unicode string.

    @param key: text to be translated
    @param locale: locale code to be used.
        If locale is None, gets the value provided by get_locale.

    """
    func_name = config.get('i18n.gettext', 'tg_gettext')
    gettext_func = dict(tg_gettext=tg_gettext,
        so_gettext=so_gettext, sa_gettext=sa_gettext).get(func_name)
    if gettext_func:
        # gettext function exists, use it :)
        return gettext_func(key, locale, domain)
    else:
        log.error("Translation disabled"
            " - i18n.gettext function %s not available", gettext_func)
        # gettext function could not be loaded?
        # Just avoid to translate and return original data.
        return key


def tg_gettext(key, locale=None, domain=None):
    """Get the gettext value for key.

    Added to builtins as '_'. Returns Unicode string.

    @param key: text to be translated
    @param locale: locale code to be used.
        If locale is None, gets the value provided by get_locale.

    """
    if locale is None:
        locale = get_locale()

    if key:
        messages = get_catalog(locale, domain)
        if messages:
            key = messages.ugettext(key)

    return key


def plain_ngettext(key1, key2, num, locale=None):
    """Translate two possible texts based on whether num is greater than 1.

    @param key1: text if num == 1
    @param key2: text if num != 1
    @param num: a number
    @type num: integer
    @locale: locale code to be used.
        If locale is None, gets the value provided by get_locale.

    """
    if num == 1:
        key = key1
    else:
        key = key2
    return plain_gettext(key, locale)


class lazystring(object):
    """Has a number of lazily evaluated functions replicating a string.

    Just override the eval() method to produce the actual value.

    """

    def __init__(self, func, *args, **kw):
        self.func = func
        self.args = args
        self.kw = kw

    def eval(self):
        return self.func(*self.args, **self.kw)

    def __unicode__(self):
        return unicode(self.eval())

    def __str__(self):
        return str(self.eval())

    def __mod__(self, other):
        return self.eval() % other

    def __cmp__(self, other):
        return cmp(self.eval(), other)

    def __eq__(self, other):
        return self.eval() == other

    def __deepcopy__(self, memo):
        return self


def lazify(func):

    def newfunc(*args, **kw):
        return lazystring(func, *args, **kw)

    return newfunc


@jsonify.when("isinstance(obj, lazystring)")
def jsonify_lazystring(obj):
    return unicode(obj)

lazy_gettext = lazify(plain_gettext)
lazy_ngettext = lazify(plain_ngettext)


def gettext(key, locale=None, domain=None):
    """Get the gettext value for key.

    Added to builtins as '_'. Returns Unicode string.

    @param key: text to be translated
    @param locale: locale code to be used.
        If locale is None, gets the value provided by get_locale.

    """
    return (request_available() and plain_gettext or lazy_gettext)(
        key, locale, domain)


def ngettext(key1, key2, num, locale=None):
    """Translate two possible texts based on whether num is greater than 1.

    @param key1: text if num==1
    @param key2: text if num!=1
    @param num: a number
    @type num: integer
    @param locale: locale code to be used.
        If locale is None, gets the value provided by get_locale.

    """
    return (request_available() and plain_ngettext or lazy_ngettext)(
        key1, key2, num, locale)


def install():
    """Add the gettext function to __builtins__ as '_'."""
    __builtins__['_'] = gettext

