"""General i18n utility functions."""

import urllib

try:
    import json
except ImportError: # Python < 2.6
    import simplejson as json
import cherrypy

from turbogears import config
from turbogears.release import version as tg_version
from turbogears.util import parse_http_accept_header, request_available


class TGURLopener(urllib.FancyURLopener):
    version = 'TurboGears/%s' % tg_version


def google_translate(from_lang, to_lang, text):
    """Translate text via the translate.google.com service.

    The source language is given by 'from_lang' and the target language as
    'to_lang'. 'text' must be a unicode or UTF-8 encoded string.

    """
    if isinstance(text, unicode):
        has_nbsp = u'\xa0' in text
        text = text.encode('utf-8')
    else:
        has_nbsp = False
    params = urllib.urlencode(dict(v='1.0',
        langpair='%s|%s' % (from_lang, to_lang), q=text))
    try:
        result = TGURLopener().open('http://ajax.googleapis.com'
            '/ajax/services/language/translate', params).read()
    except IOError:
        text = None
    else:
        try:
            result = json.loads(result)
        except ValueError:
            text = None
        else:
            try:
                text = result['responseData']['translatedText']
            except (KeyError, TypeError):
                text = None
            else:
                if text and not has_nbsp:
                    text = text.replace(u'\xa0', ' ')
    return text


def lang_in_gettext_format(lang):
    if len(lang) > 2:
        country = lang[3:].upper()
        lang = lang[:2] + '_' + country
    return lang


def get_accept_languages(accept):
    """Get the list of accepted languages, by order of preference.

    THis is based on the HTTP Accept-Language string. See W3C RFC 2616
    (http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html) for specification.

    """
    langs = parse_http_accept_header(accept)
    for index, lang in enumerate(langs):
        langs[index] = lang_in_gettext_format(lang)
    return langs


def get_locale(locale=None):
    """Get the user locale.

    This is done using _get_locale or an app-specific locale lookup function.

    """
    if not locale:
        get_locale_f = config.get('i18n.get_locale', _get_locale)
        locale = get_locale_f()
    return locale


def _get_locale():
    """Default function for returning the locale.

    First it looks in the session for a locale key, then it checks the HTTP
    Accept-Language header, and finally it checks the config default locale
    setting. This can be replaced by your own function by setting the CherryPy
    config setting i18n.get_locale to your function name.

    """
    if not request_available():
        return config.get('i18n.default_locale', 'en')

    if config.get('tools.sessions.on', False):
        session_key = config.get('i18n.session_key', 'locale')
        locale = cherrypy.session.get(session_key)
        if locale:
            return locale
    browser_accept_lang = _get_locale_from_accept_header()
    return browser_accept_lang or config.get('i18n.default_locale', 'en')


def _get_locale_from_accept_header():
    """Check HTTP Accept-Language header to find the preferred language."""
    try:
        header = cherrypy.request.headers.get('Accept-Language')
        if header:
            accept_languages = get_accept_languages(header)
            if accept_languages:
                return accept_languages[0]
    except AttributeError:
        pass


def set_session_locale(locale):
    """Set the i18n session locale.

    Raises an error if session support is not enabled.

    """
    session_key = config.get('i18n.session_key', 'locale')
    cherrypy.session[session_key] = locale
