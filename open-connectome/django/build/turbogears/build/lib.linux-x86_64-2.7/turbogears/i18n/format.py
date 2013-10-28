"""Localized formatting functions.

These functions extract localization data from config files located
in the data/directory.

"""

import os
import re
from operator import itemgetter
from warnings import filterwarnings

import pkg_resources

from turbogears.i18n.utils import get_locale

try:
    # locale modules can have same name as locale directories
    filterwarnings('ignore', message="Not importing directory",
        category=ImportWarning, module='turbogears.i18n')
except NameError: # Python < 2.5
    pass # does not have ImportWarning anyway


def is_locale_format(locale):
    """Check if locale is supported."""
    py_filename = pkg_resources.resource_filename(
        'turbogears.i18n.data', '%s.py' % locale)
    if os.path.exists(py_filename):
        return True
    pyc_filename = pkg_resources.resource_filename(
        'turbogears.i18n.data', '%s.pyc' % locale)
    if os.path.exists(pyc_filename):
        return True
    return False


def get_locale_module(locale):
    """Get i18n module supporting the locale."""
    try:
        # check if locale is supported. If not, check again with
        # first part of locale for example, 'fi_FI' > 'fi'.
        if not is_locale_format(locale):
            locale = locale[:2]
        name = 'turbogears.i18n.data.%s' % locale
        mod = __import__(name)
        parts = name.split('.')[1:]
        for p in parts:
            mod = getattr(mod, p)
        return mod
    except (ImportError, AttributeError):
        return None


def get(locale, name, default=None):
    """Get an attribute value for the locale."""
    locale = get_locale(locale)
    mod = get_locale_module(locale)
    return getattr(mod, name, default)


def get_countries(locale=None):
    """Get all supported countries.

    Returns a list of tuples, consisting of international country code
    and localized name, e.g. ('AU', 'Australia').

    """
    countries = get(locale, 'countries', {}).items()
    countries.sort(key=itemgetter(1))
    return countries


def get_country(key, locale=None):
    """Get localized name of country based on international country code."""
    return get(locale, 'countries', {})[key]


def get_languages(locale=None):
    """Get all supported languages.

    Returns a list of tuples, with language code and localized name,
    e.g. ('en', 'English').

    """
    languages = get(locale, 'languages', {}).items()
    languages.sort(key=itemgetter(1))
    return languages


def get_language(key, locale=None):
    """Get localized name of language based on language code."""
    return get(locale, 'languages', {})[key]


def get_month_names(locale=None):
    """Get list of full month names, starting with January."""
    return get(locale, 'months', [])


def get_abbr_month_names(locale=None):
    """Get list of abbreviated month names, starting with Jan."""
    return get(locale, 'abbrMonths', [])


def get_weekday_names(locale=None):
    """Get list of full weekday names."""
    return get(locale, 'days', [])


def get_abbr_weekday_names(locale=None):
    """Get list of abbreviated weekday names."""
    return get(locale, 'abbrDays', get_weekday_names(locale))


def get_decimal_format(locale=None):
    """Get decimal point for the locale."""
    return get(locale, 'numericSymbols', {}).get('decimal', '.')


def get_group_format(locale=None):
    """Get digit group separator for thousands for the locale."""
    return get(locale, 'numericSymbols', {}).get('group', ',')


def format_number(value, locale=None):
    """Get number formatted with grouping for thousands.

    E.g. 5000000 will be formatted as 5,000,000.

    """
    gf = get_group_format(locale)
    thou = re.compile(r'([0-9])([0-9][0-9][0-9]([%s]|$))' % gf).search
    v = str(value)
    mo = thou(v)
    while mo is not None:
        i = mo.start(0)
        v = v[:i+1] + gf + v[i+1:]
        mo = thou(v)
    return unicode(v)


def format_decimal(value, num_places, locale=None):
    """Get number formatted with grouping for thousands and decimal places.

    E.g. 5000000.898 will be formatted as 5,000,000.898.

    """
    v = ('%%.%df' % num_places) % value
    if num_places == 0:
        return format_number(v, locale=locale)
    num, decimals = v.split('.', 1)
    return format_number(num, locale) + unicode(
        get_decimal_format(locale) + decimals)


def format_currency(value, locale=None):
    """Get formatted currency value."""
    return format_decimal(value, 2, locale)


def parse_number(value, locale=None):
    """Take localized number string and return a long integer.

    Throws ValueError if bad format.

    """
    return long(value.replace(get_group_format(locale), ""))


def parse_decimal(value, locale=None):
    """Take localized decimal string and return a float.

    Throws ValueError if bad format.

    """
    value = value.replace(get_group_format(locale), '')
    value = value.replace(get_decimal_format(locale), '.')
    return float(value)


def get_date_format(format, locale=None):
    """Get localized date format."""
    formats = get(locale, 'dateFormats', {})
    return formats.get(format, None)


def format_date(dt, format='medium', locale=None,
        time_format='', date_format=''):
    """Get formatted date value.

    format can be "full", "long", "medium" or "short".
    To have complete control over formatting,
    use time_format and date_format parameters.

    @param dt: datetime
    @type dt: datetime.datetime

    @param format: format('full', 'long', 'medium', 'short')
    @type format: string

    @param locale: the locale
    @type locale: string

    @param time_format: standard time formatting string, e.g. %H:%M
    @type time_format:s tring

    @param time_format: date formatting template string.
    Template variables include standard date formatting string like %d or %Y
    plus a few locale-specific names:
    %%(abbrmonthname)s, %%(dayname)s, %%(abbrmonthname)s and %%(monthname)s.
    @type time_format: string

    """
    pattern = date_format or get_date_format(format, locale)
    if not pattern:
        return str(dt)
    month = dt.month - 1
    weekday = dt.weekday()
    # becasue strftime() accepts str only but not unicode,
    # we encode string to utf-8 and then decode back
    date_str = dt.strftime(pattern.encode('utf8') + time_format)
    return date_str.decode('utf8') % dict(
        monthname=get_month_names(locale)[month],
        abbrmonthname=get_abbr_month_names(locale)[month],
        dayname=get_weekday_names(locale)[weekday],
        abbrdayname=get_abbr_weekday_names(locale)[weekday])
