"""Convenient validators and converters for data coming in from the web.

This module also imports everything from formencode.validators, so all
common validation routines are available here."""

import time
import re
from datetime import datetime
import warnings

try:
    import json
except ImportError: # Python < 2.6
    import simplejson as json

from formencode import ForEach
from formencode import validators # to disambiguate the Number validator...
from formencode import national

from formencode.validators import *
from formencode.compound import *
from formencode.api import Invalid, NoDefault
from formencode.schema import Schema

from turbojson import jsonify

from turbogears import util
from turbogears.i18n import format


def _(s): return s # dummy

# FormEncode should call TG's gettext function with domain = "FormEncode"
Validator.gettextargs['domain'] = 'FormEncode'


# Validators handling country names and/or languages

def StateProvince(*kw, **kwargs):
    warnings.warn("Please use national.USStateProvince",
        DeprecationWarning, 2)
    return national.USStateProvince(*kw, **kwargs)

def PhoneNumber(*kw, **kwargs):
    warnings.warn("Please use national.USPhoneNumber",
        DeprecationWarning, 2)
    return national.USPhoneNumber(*kw, **kwargs)

def PostalCode(*kw, **kwargs):
    warnings.warn("Please use national.USPostalCode",
        DeprecationWarning, 2)
    return national.USPostalCode(*kw, **kwargs)

def IPhoneNumberValidator(*kw, **kwargs):
    warnings.warn("Please use national.InternationalPhoneNumber",
        DeprecationWarning, 2)
    return national.InternationalPhoneNumber(*kw, **kwargs)


class TgFancyValidator(FancyValidator):
    gettextargs = {'domain': 'TurboGears'}


class Money(TgFancyValidator):
    """Validate a monetary value with currency."""

    messages = {
        'badFormat': _('Invalid number format'),
        'empty': _('Empty values not allowed'),
    }

    def _to_python(self, value, state):
        """Parse a string and return a float or integer."""
        try:
            return format.parse_decimal(value)
        except ValueError:
            raise Invalid(self.message('badFormat', state), value, state)

    def _from_python(self, value, state):
        """Return a string using the correct grouping."""
        return format.format_currency(value)


class Number(TgFancyValidator):
    """Validate a decimal number."""

    decimals = None

    def _to_python(self, value, state):
        """Parse a string and return a float or integer."""
        if isinstance(value, basestring):
            try:
                value = format.parse_decimal(value)
            except ValueError:
                pass
        return validators.Number.to_python(value, state)

    def _from_python(self, value, state):
        """Return a string using the correct grouping.

        If the validator was instantiated with a decimals parameter,
        this is used for the number  of decimals. If None ist given,
        the number of decimals is determined by the value itself.

        """
        if self.decimals is None:
            decimals = util.find_precision(value)
        else:
            decimals = self.decimals
        if decimals > 0:
            return format.format_decimal(value, decimals)
        else:
            return format.format_number(value)


class DateTimeConverter(TgFancyValidator):
    """Convert between Python datetime objects and strings."""

    format="%Y/%m/%d %H:%M"

    messages = {
        'badFormat': _('Invalid datetime format'),
        'empty': _('Empty values not allowed'),
    }

    def _to_python(self, value, state):
        """Parse a string and return a datetime object."""
        if value and isinstance(value, datetime):
            return value
        else:
            try:
                format = self.format
                if callable(format):
                    format = format()
                tpl = time.strptime(value, format)
            except ValueError:
                raise Invalid(self.message('badFormat', state), value, state)
            # shoudn't use time.mktime() because it can give OverflowError,
            # depending on the date (e.g. pre 1970) and underlying C library
            return datetime(year=tpl.tm_year, month=tpl.tm_mon, day=tpl.tm_mday,
                    hour=tpl.tm_hour, minute=tpl.tm_min, second=tpl.tm_sec)

    def _from_python(self, value, state):
        """Return a string representation of a datetime object."""
        if not value:
            return None
        elif isinstance(value, datetime):
            # Python stdlib can only handle dates with year greater than 1900
            format = self.format
            if callable(format):
                format = format()
            if format is None:
                format = "%Y-%m-%d"
            if value.year <= 1900:
                return strftime_before1900(value, format)
            else:
                return value.strftime(format)
        else:
            return value


# Improved FieldStorageUploadConverter heeding not_empty=False
# (see TurboGears ticket #1705, FormEncode bug #1905250)

class FieldStorageUploadConverter(TgFancyValidator):

    messages = {
        'notEmpty': _("Filename must not be empty"),
        }

    def _to_python(self, value, state=None):
        try:
            filename = value.filename
        except AttributeError:
            filename = None
        if not filename and self.not_empty:
            raise Invalid(self.message('notEmpty', state), value, state)
        return value


# For translated messages that are not wrapped in a Validator.messages
# dictionary, we need to reinstate the TurboGears gettext function under
# the name "_", with the "TurboGears" domain, so that the TurboGears.mo
# file is selected.
import turbogears.i18n
_ = lambda s: turbogears.i18n.gettext(s, domain='TurboGears')


class MultipleSelection(ForEach):
    """A default validator for SelectionFields with multiple selection."""

    if_missing = NoDefault
    if_empty = []

    def to_python(self, value, state=None):
        try:
            return super(MultipleSelection, self).to_python(value, state)
        except Invalid:
            raise Invalid(_("Please select at least a value"), value, state)


class Schema(Schema):
    """Modified Schema validator for TurboGears.

    A schema validates a dictionary of values, applying different validators
    (by key) to the different values.

    This modified Schema allows fields that do not appear in the fields
    parameter of your schema, but filters them out from the value dictionary.
    You might want to set filter_extra_fields to True when you're building a
    dynamic form with unpredictable keys and need these values.

    """

    filter_extra_fields = True
    allow_extra_fields = True
    if_key_missing = None

    def from_python(self, value, state=None):
        # The Schema shouldn't do any from_python conversion because
        # adjust_value already takes care of that for all childs.
        return value


class JSONValidator(TgFancyValidator):
    """A validator for JSON format."""

    def _from_python(self, value, state):
        return jsonify.encode(value)

    def _to_python(self, value, state):
        return json.loads(value)


# Auxiliary functions

def _findall(text, substr):
    # Also finds overlaps
    sites = []
    i = 0
    while 1:
        j = text.find(substr, i)
        if j == -1:
            break
        sites.append(j)
        i = j+1
    return sites

_illegal_s = re.compile(r"((^|[^%])(%%)*%s)")

def strftime_before1900(dt, fmt):
    """strftime implementation supporting proleptic Gregorian dates before 1900.

    @see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/306860

    """
    if _illegal_s.search(fmt):
        raise TypeError("This strftime implementation does not handle %s")
    if dt.year > 1900:
        return dt.strftime(fmt)

    year = dt.year
    # For every non-leap year century, advance by
    # 6 years to get into the 28-year repeat cycle
    delta = 2000 - year
    off = 6*(delta // 100 + delta // 400)
    year += off

    # Move to around the year 2000
    year = year + ((2000 - year)//28)*28
    timetuple = dt.timetuple()
    s1 = time.strftime(fmt, (year,) + timetuple[1:])
    sites1 = _findall(s1, str(year))

    s2 = time.strftime(fmt, (year+28,) + timetuple[1:])
    sites2 = _findall(s2, str(year+28))

    sites = []
    for site in sites1:
        if site in sites2:
            sites.append(site)

    s = s1
    syear = "%4d" % (dt.year,)
    for site in sites:
        s = s[:site] + syear + s[site+4:]
    return s
