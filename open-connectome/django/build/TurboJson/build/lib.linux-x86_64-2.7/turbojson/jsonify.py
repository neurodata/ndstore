"""JSON encoding functions using PEAK-Rules."""

from datetime import date, datetime
from decimal import Decimal

from peak.rules import abstract, around, when

# simplejson is actually available as json in the standard library
# since Python 2.6, but the externally maintained package is newer
# and can be substantially faster, so we try to import this first
try:
    from simplejson import JSONEncoder # externally maintained version
except ImportError:
    from json import JSONEncoder # standard lib version

__all__ = ['jsonify', 'encode', 'encode_iter']


# Global options

descent_bases = True


# Specific encoding functions

def jsonify(obj):
    """Generic function for converting objects to JSON.

    Specific functions should return a string or an object that can be
    serialized with JSON, i.e., it is made up of only lists, dictionaries
    (with string keys), strings, ints, and floats.

    """
    return jsonify_default(obj)

# This is for easier usage and backward compatibility:
jsonify.when = when.__get__(jsonify)
jsonify.around = around.__get__(jsonify)


# Explicit encoding function

@jsonify.around("hasattr(obj, '__json__')")
def jsonify_explicit(obj):
    """JSONify objects with explicit JSONification method."""
    return obj.__json__()


# Default encoding functions

@abstract
def jsonify_default(obj):
    """Default JSONify method for Python objects."""
    return NotImplementedError

jsonify_default.when = when.__get__(jsonify_default)
jsonify_default.around = around.__get__(jsonify_default)

@jsonify_default.when("obj is None"
    " or isinstance(obj, (basestring, bool, int, long, float, list, dict))")
def jsonify_serializable(obj):
    """JSONify simple serializable objects."""
    return obj

@jsonify_default.when("isinstance(obj, (set, frozenset, tuple))")
def jsonify_list_like(obj):
    """JSONify simple list-like objects."""
    return list(obj)

@jsonify_default.when("isinstance(obj, Decimal)")
def jsonify_decimal(obj):
    """JSONify Decimal objects."""
    return float(obj)

@jsonify.when("isinstance(obj, (date, datetime))")
def jsonify_datetime(obj):
    """JSONify date and datetime objects."""
    return str(obj)


# SQLObject support

try:
    from sqlobject import SQLObject

    def _sqlobject_attrs(obj):
        """Get all attributes of an SQLObject."""
        sm = obj.__class__.sqlmeta
        try:
            while sm is not None:
                # we need to exclude the ID-keys, as for some reason
                # this won't work for subclassed items
                for key in sm.columns:
                    if key[-2:] != 'ID':
                        yield key
                sm = descent_bases and sm.__base__ or None
        except AttributeError: # happens if we descent to <type object>
            pass

    def is_sqlobject(obj):
        return (isinstance(obj, SQLObject)
            and hasattr(obj.__class__, 'sqlmeta'))

    @jsonify_default.when("is_sqlobject(obj)")
    def jsonify_sqlobject(obj):
        """JSONify SQLObjects."""
        result = {'id': obj.id}
        for name in _sqlobject_attrs(obj):
            result[name] = getattr(obj, name)
        return result

    try:
        SelectResultsClass = SQLObject.SelectResultsClass
    except AttributeError:
        pass
    else:

        @jsonify_default.when("isinstance(obj, SelectResultsClass)")
        def jsonify_select_results(obj):
            """JSONify SQLObject.SelectResults."""
            return list(obj)

except ImportError:
    pass


# SQLAlchemy support

try:
    import sqlalchemy

    try:
        import sqlalchemy.ext.selectresults
        from sqlalchemy.util import OrderedProperties
    except ImportError: # SQLAlchemy >= 0.5

        def is_saobject(obj):
            return hasattr(obj, '_sa_class_manager')

        @jsonify_default.when("is_saobject(obj)")
        def jsonify_saobject(obj):
            """JSONify SQLAlchemy objects."""
            props = {}
            for key in obj.__dict__:
                if not key.startswith('_sa_'):
                    props[key] = getattr(obj, key)
            return props

    else: # SQLAlchemy < 0.5

        def is_saobject(obj):
            return (hasattr(obj, 'c')
                and isinstance(obj.c, OrderedProperties))

        @jsonify_default.when("is_saobject(obj)")
        def jsonify_saobject(obj):
            """JSONify SQLAlchemy objects."""
            props = {}
            for key in obj.c.keys():
                props[key] = getattr(obj, key)
            return props

        try:
            from sqlalchemy.orm.attributes import InstrumentedList
        except ImportError: # SQLAlchemy >= 0.4
            pass # normal lists are used here

        else: # SQLAlchemy < 0.4

            @jsonify_default.when("isinstance(obj, InstrumentedList)")
            def jsonify_instrumented_list(obj):
                """JSONify SQLAlchemy instrumented lists."""
                return list(obj)

    from sqlalchemy.engine.base import ResultProxy, RowProxy

    @jsonify_default.when("isinstance(obj, ResultProxy)")
    def jsonify_saproxy(obj):
        return list(obj)

    @jsonify_default.when("isinstance(obj, RowProxy)")
    def jsonify_saproxy(obj):
        return dict(obj)

except ImportError:
    pass


# JSON encoder class

class GenericJSON(JSONEncoder):

    def __init__(self, **opts):
        opt = opts.pop('descent_bases', None)
        if opt is not None:
            global descent_bases
            descent_bases = opt
        super(GenericJSON, self).__init__(**opts)

    def default(self, obj):
        return jsonify(obj)

_instance = GenericJSON()


# General encoding functions

def encode(obj):
    """Return a JSON string representation of a Python object."""
    return _instance.encode(obj)

def encode_iter(obj):
    """Encode object, yielding each string representation as available."""
    return _instance.iterencode(obj)
