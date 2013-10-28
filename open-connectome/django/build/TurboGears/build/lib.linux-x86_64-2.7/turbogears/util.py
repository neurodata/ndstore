"""The TurboGears utility module."""

_all__ = ['Bunch', 'DictObj', 'DictWrapper', 'Enum', 'setlike',
   'get_package_name', 'get_model', 'load_project_config',
   'ensure_sequence', 'has_arg', 'to_kw', 'from_kw', 'adapt_call',
   'call_on_stack', 'remove_keys', 'arg_index',
   'inject_arg', 'inject_args', 'add_tg_args', 'bind_args',
   'recursive_update', 'combine_contexts',
   'request_available', 'flatten_sequence', 'load_class',
   'parse_http_accept_header', 'simplify_http_accept_header',
   'to_unicode', 'to_utf8', 'quote_cookie', 'unquote_cookie',
   'get_template_encoding_default', 'get_mime_type_for_format',
   'mime_type_has_charset', 'find_precision', 'copy_if_mutable',
   'match_ip', 'deprecated']

import os
import sys
import re
import logging
import warnings
import htmlentitydefs
import socket
import struct
from inspect import getargspec, getargvalues
from itertools import izip, islice, chain
from operator import isSequenceType
from Cookie import _quote as quote_cookie, _unquote as unquote_cookie

import pkg_resources

from cherrypy import request

from turbogears.decorator import decorator
from turbogears import config


def deprecated(message=None):
    """Decorator which can be used to mark functions as deprecated.

    It will result in a warning being emitted when the function is used.

    Inspired by http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/391367

    """
    def decorate(func):
        if not decorate.message:
            decorate.message = ("Call to deprecated function %s."
                % func.__name__)
        def new_func(*args, **kwargs):
            if not decorate.warned:
                warnings.warn(decorate.message, category=DeprecationWarning,
                    stacklevel=2)
                decorate.warned = True
            return func(*args, **kwargs)
        new_func.__name__ = func.__name__
        new_func.__doc__ = func.__doc__
        new_func.__dict__.update(func.__dict__)
        return new_func
    decorate.message = message
    decorate.warned = False
    return decorate


def missing_dependency_error(name=None):
    msg = """\
Before you can run this command, you need to install all the project's
dependencies by running "python setup.py develop" in the project directory, or
you can install the application with "python setup.py install", or build an egg
with "python setup.py bdist_egg" and install it with "easy_install dist/<egg>".

If you are stuck, visit http://docs.turbogears.org/GettingHelp for support."""
    if name:
        msg = ("This project requires the %s package but it could not be "
            "found.\n\n" % name) + msg
    return msg


class Bunch(dict):
    """Simple but handy collector of a bunch of named stuff."""

    def __repr__(self):
        keys = self.keys()
        keys.sort()
        args = ', '.join(['%s=%r' % (key, self[key]) for key in keys])
        return '%s(%s)' % (self.__class__.__name__, args)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    __setattr__ = dict.__setitem__

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)


class DictObj(Bunch):

    @deprecated("Use Bunch instead of DictObj and DictWrapper.")
    def __init__(self, *args, **kw):
        super(DictObj, self).__init__(*args, **kw)

DictWrapper = DictObj


def Enum(*names):
    """True immutable symbolic enumeration with qualified value access.

    Written by Zoran Isailovski:
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/413486

    """

    # Uncomment the following check if you don't like empty enums.
    # if not names:
    #     raise ValueError("Empty enums are not supported")

    class EnumClass(object):
        __slots__ = names
        def __iter__(self):
            return iter(constants)
        def __len__(self):
            return len(constants)
        def __getitem__(self, i):
            return constants[i]
        def __repr__(self):
            return 'Enum' + str(names)
        def __str__(self):
            return 'enum ' + str(constants)

    enumType = EnumClass()

    class EnumValue(object):
        __slots__ = ('__value')
        def __init__(self, value):
            self.__value = value
        Value = property(lambda self: self.__value)
        EnumType = property(lambda self: enumType)
        def __hash__(self):
            return hash(self.__value)
        def __cmp__(self, other):
            # C fans might want to remove the following check
            # to make all enums comparable by ordinal value
            if not (isinstance(other, EnumValue)
                    and self.EnumType is other.EnumType):
                raise TypeError("Only values from the same enum are comparable")
            return cmp(self.__value, other.__value)
        def __invert__(self):
            return constants[maximum - self.__value]
        def __nonzero__(self):
            return bool(self.__value)
        def __repr__(self):
            return str(names[self.__value])

    maximum = len(names) - 1
    constants = [None] * len(names)
    for i, each in enumerate(names):
        val = EnumValue(i)
        setattr(EnumClass, each, val)
        constants[i] = val
    constants = tuple(constants)
    return enumType


class setlike(list):
    """Set preserving item order."""

    def add(self, item):
        if item not in self:
            self.append(item)

    def add_all(self, iterable):
        for item in iterable:
            self.add(item)


def get_project_meta(name):
    """Get egg-info file with that name in the current project."""
    for dirname in os.listdir('./'):
        if dirname.lower().endswith('egg-info'):
            fname = os.path.join(dirname, name)
            return fname


def get_project_config():
    """Try to select appropriate project configuration file."""
    return os.path.exists('setup.py') and 'dev.cfg' or 'prod.cfg'


def load_project_config(configfile=None):
    """Try to update the project settings from the config file specified.

    If configfile is C{None}, uses L{get_project_config} to locate one.

    """
    if configfile is None:
        configfile = get_project_config()
    if not os.path.isfile(configfile):
        print 'Config file %s not found or is not a file.' % (
            os.path.abspath(configfile),)
        sys.exit()
    package = get_package_name()
    config.update_config(configfile=configfile,
        modulename = package + '.config')


def get_package_name():
    """Try to find out the package name of the current directory."""
    package = config.get('package')
    if package:
        return package
    if hasattr(sys, 'argv') and "--egg" in sys.argv:
        projectname = sys.argv[sys.argv.index("--egg")+1]
        egg = pkg_resources.get_distribution(projectname)
        top_level = egg._get_metadata("top_level.txt")
    else:
        fname = get_project_meta('top_level.txt')
        top_level = fname and open(fname) or []
    for package in top_level:
        package = package.rstrip()
        if package and package != 'locales':
            return package


def get_project_name():
    pkg_info = get_project_meta('PKG-INFO')
    if pkg_info:
        name = list(open(pkg_info))[1][6:-1]
        return name.strip()


def get_model():
    package_name = get_package_name()
    if not package_name:
        return None
    package = __import__(package_name, {}, {}, ["model"])
    if hasattr(package, "model"):
        return package.model


def ensure_sequence(obj):
    """Construct a sequence from object."""
    if obj is None:
        return []
    elif isSequenceType(obj):
        return obj
    else:
        return [obj]


def to_kw(func, args, kw, start=0):
    """Convert all applicable arguments to keyword arguments."""
    argnames, defaults = getargspec(func)[::3]
    defaults = ensure_sequence(defaults)
    kv_pairs = izip(
        islice(argnames, start, len(argnames) - len(defaults)), args)
    for k, v in kv_pairs:
        kw[k] = v
    return args[len(argnames)-len(defaults)-start:], kw


def from_kw(func, args, kw, start=0):
    """Extract named positional arguments from keyword arguments."""
    argnames, defaults = getargspec(func)[::3]
    defaults = ensure_sequence(defaults)
    newargs = [kw.pop(name) for name in islice(argnames, start,
        len(argnames) - len(defaults)) if name in kw]
    newargs.extend(args)
    return newargs, kw


def adapt_call(func, args, kw, start=0):
    """Remove unsupported func arguments from given args list and kw dict.

    @param func: the callable to inspect for supported arguments
    @type func: callable

    @param args: the names of the positional arguments intended to be passed
    to func
    @type args: list

    @param kw: the keyword arguments intended to be passed to func
    @type kw: dict

    @keyparam start: the number of items from the start of the argument list of
    func to disregard. Set start=1 to use adapt_call on a bound method to
    disregard the implicit self argument.

    @type start: int

    Returns args list and kw dict from which arguments unsupported by func
    have been removed. The passed in kw dict is also stripped as a side-effect.
    The returned objects can then be used to call the target function.

    Example:

        def myfunc(arg1, arg2, kwarg1='foo'):
            pass

        args, kw = adapt_call(myfunc, ['args1, 'bogus1'],
           {'kwargs1': 'bar', 'bogus2': 'spamm'})
        # --> ['args1'], {'kwargs1': 'bar'}
        myfunc(*args, **kw)

    """
    argnames, varargs, kwargs = getargspec(func)[:3]
    del argnames[:start]
    if kwargs in (None, "_decorator__kwargs"):
        remove_keys(kw, [key for key in kw if key not in argnames])
    if varargs in (None, "_decorator__varargs"):
        args = args[:len(argnames)]
    for n, key in enumerate(argnames):
        if key in kw:
            args = args[:n]
            break
    return args, kw


def call_on_stack(func_name, kw, start=0):
    """Check if a call to function matching pattern is on stack."""
    try:
        frame = sys._getframe(start+1)
    except ValueError:
        return False
    while frame.f_back:
        frame = frame.f_back
        if frame.f_code.co_name == func_name:
            args = getargvalues(frame)[3]
            for key in kw.iterkeys():
                try:
                    if kw[key] != args[key]:
                        break
                except (KeyError, TypeError):
                    break
            else:
                return True
    return False


def remove_keys(dict_, seq):
    """Gracefully remove keys from dict."""
    for key in seq:
        dict_.pop(key, None)
    return dict_


def has_arg(func, argname):
    """Check whether function has argument."""
    return argname in getargspec(func)[0]


def arg_index(func, argname):
    """Find index of argument as declared for given function."""
    argnames = getargspec(func)[0]
    if has_arg(func, argname):
        return argnames.index(argname)
    else:
        return None


def inject_arg(func, argname, argval, args, kw, start=0):
    """Insert argument into call."""
    argnames, defaults = getargspec(func)[::3]
    defaults = ensure_sequence(defaults)
    pos = arg_index(func, argname)
    if pos is None or pos > len(argnames) - len(defaults) - 1:
        kw[argname] = argval
    else:
        pos -= start
        args = tuple(chain(islice(args, pos), (argval,),
            islice(args, pos, None)))
    return args, kw


def inject_args(func, injections, args, kw, start=0):
    """Insert arguments into call."""
    for argname, argval in injections.iteritems():
        args, kw = inject_arg(func, argname, argval, args, kw, start)
    return args, kw


def inject_call(func, injections, *args, **kw):
    """Insert arguments and call."""
    args, kw = inject_args(func, injections, args, kw)
    return func(*args, **kw)


def add_tg_args(func, args):
    """Add hint for special arguments that shall not be removed."""
    try:
        tg_args = func._tg_args
    except AttributeError:
        tg_args = set()
    tg_args.update(args)
    func._tg_args = tg_args


def bind_args(**add):
    """Call with arguments set to a predefined value."""
    def entagle(func):
        return lambda func, *args, **kw: inject_call(func, add, *args, **kw)

    def make_decorator(func):
        argnames, varargs, kwargs, defaults = getargspec(func)
        defaults = list(ensure_sequence(defaults))
        defaults = [d for d in defaults if
            argnames[-len(defaults) + defaults.index(d)] not in add]
        argnames = [arg for arg in argnames if arg not in add]
        return decorator(entagle, (argnames, varargs, kwargs, defaults))(func)

    return make_decorator


def recursive_update(to_dict, from_dict):
    """Recursively update all dicts in to_dict with values from from_dict."""
    # probably slow as hell :( should be optimized somehow...
    for k, v in from_dict.iteritems():
        if isinstance(v, dict) and isinstance(to_dict[k], dict):
            recursive_update(to_dict[k], v)
        else:
            to_dict[k] = v
    return to_dict


def combine_contexts(frames=None, depth=None):
    """Combine contexts (globals, locals) of frames."""
    locals_ = {}
    globals_ = {}
    if frames is None:
        frames = []
    if depth is not None:
        frames.extend([sys._getframe(d+1) for d in depth])
    for frame in frames:
        locals_.update(frame.f_locals)
        globals_.update(frame.f_globals)
    return locals_, globals_


def request_available():
    """Check if cherrypy.request is available."""
    stage = getattr(request, 'stage', None)
    return stage is not None


def flatten_sequence(seq):
    """Flatten sequence."""
    for item in seq:
        if isSequenceType(item) and not isinstance(item, basestring):
            for item in flatten_sequence(item):
                yield item
        else:
            yield item


def load_class(dottedpath):
    """Load a class from a module in dotted-path notation.

    E.g.: load_class("package.module.class").

    Based on recipe 16.3 from Python Cookbook, 2ed., by Alex Martelli,
    Anna Martelli Ravenscroft, and David Ascher (O'Reilly Media, 2005)

    """
    assert dottedpath is not None, "dottedpath must not be None"
    splitted_path = dottedpath.split('.')
    modulename = '.'.join(splitted_path[:-1])
    classname = splitted_path[-1]
    try:
        try:
            module = __import__(modulename, globals(), locals(), [classname])
        except ValueError: # Py < 2.5
            if not modulename:
                module = __import__(__name__.split('.', 1)[0],
                    globals(), locals(), [classname])
    except ImportError:
        # properly log the exception information and return None
        # to tell caller we did not succeed
        logging.exception('tg.utils: Could not import %s'
            ' because an exception occurred', dottedpath)
        return None
    try:
        return getattr(module, classname)
    except AttributeError:
        logging.exception('tg.utils: Could not import %s'
            ' because the class was not found', dottedpath)
        return None


def parse_http_accept_header(accept):
    """Parse an HTTP Accept header (RFC 2616) into a sorted list.

    The quality factors in the header determine the sort order.
    The values can include possible media-range parameters.
    This function can also be used for the Accept-Charset,
    Accept-Encoding and Accept-Language headers.

    """
    if accept is None:
        return []
    items = []
    for item in accept.split(','):
        params = item.split(';')
        for i, param in enumerate(params[1:]):
            param = param.split('=', 1)
            if param[0].strip() == 'q':
                try:
                    q = float(param[1])
                    if not 0 < q <= 1:
                        raise ValueError
                except (IndexError, ValueError):
                    q = 0
                else:
                    item = ';'.join(params[:i+1])
                break
        else:
            q = 1
        if q:
            item = item.strip()
            if item:
                items.append((item, q))
    items.sort(key=lambda item: -item[1])
    return [item[0] for item in items]


def simplify_http_accept_header(accept):
    """Parse an HTTP Accept header (RFC 2616) into a preferred value.

    The quality factors in the header determine the preference.
    Possible media-range parameters are allowed, but will be ignored.
    This function can also be used for the Accept-Charset,
    Accept-Encoding and Accept-Language headers.

    This is similar to parse_http_accept_header(accept)[0], but faster.

    """
    if accept is None:
        return None
    best_item = accept
    best_q = 0
    for item in accept.split(','):
        params = item.split(';')
        item = params.pop(0)
        for param in params:
            param = param.split('=', 1)
            if param[0].strip() == 'q':
                try:
                    q = float(param[1])
                    if not 0 < q <= 1:
                        raise ValueError
                except (IndexError, ValueError):
                    q = 0
                break
        else:
            q = 1
        if q > best_q:
            item = item.strip()
            if item:
                best_item = item
                if q == 1:
                    break
                best_q = q
    return best_item


def to_unicode(value):
    """Convert encoded string to unicode string.

    Uses get_template_encoding_default() to guess source string encoding.
    Handles turbogears.i18n.lazystring correctly.

    """
    if isinstance(value, str):
        # try to make sure we won't get UnicodeDecodeError from the template
        # by converting all encoded strings to Unicode strings
        try:
            value = unicode(value)
        except UnicodeDecodeError:
            try:
                value = unicode(value, get_template_encoding_default())
            except UnicodeDecodeError:
                # fail early
                raise ValueError("Non-unicode string: %r" % value)
    return value


def to_utf8(value):
    """Convert a unicode string to utf-8 encoded plain string.

    Handles turbogears.i18n.lazystring correctly.

    Does nothing to already encoded string.

    """
    if isinstance(value, str):
        pass
    elif hasattr(value, '__unicode__'):
        value = unicode(value)
    if isinstance(value, unicode):
        value = value.encode('utf-8')
    return value


def get_template_encoding_default(engine_name=None):
    """Return default encoding for template files (Kid, Genshi, etc.)."""
    if engine_name is None:
        engine_name = config.get('tg.defaultview', 'genshi')
    return config.get('%s.encoding' % engine_name,
        config.get('%s.default_encoding' % engine_name, 'utf-8'))


_format_mime_types = dict(
    plain='text/plain', text='text/plain',
    html='text/html', xhtml = 'text/html', # see note below
    xml='text/xml', json='application/json')

def get_mime_type_for_format(format):
    """Return default MIME media type for a template format.

    Note: By default we are serving xhtml as "text/html" instead of the more
    correct "application/xhtml+xml", since many browsers, particularly MSIE,
    do not support this. We are assuming that xhtml means XHTML 1.0 here,
    where this approach is possible. It would be possible to use some kind
    of content negotiation to deliver a customized content type, but we avoid
    this because it causes more harm (e.g. with proxies involved) than good.

    If you want to serve the proper content type (e.g. for XHTML 1.1),
    set tg.format_mime_types= {'xhtml': 'application/xhtml+xml'}.
    You can also set a particular content type per controller using the
    content_type parameter of the expose decorator.

    For detailed information about this issues, see here:
    http://www.smackthemouse.com/xhtmlxml, http://schneegans.de/web/xhtml/.

    """
    mime_type = config.get('tg.format_mime_types', {}).get(format)
    if not mime_type:
        mime_type = _format_mime_types.get(format, 'text/html')
    return mime_type


def mime_type_has_charset(mime_type):
    """Return whether the MIME media type supports a charset parameter.

    Note: According to RFC4627, we do not output a charset parameter
    for "application/json" (this type always uses a UTF encoding).

    """
    if not mime_type:
        return False
    if mime_type.startswith('text/'):
        return True
    if mime_type.startswith('application/'):
        if mime_type.endswith('/xml') or mime_type.endswith('+xml'):
            return True
        if mime_type.endswith('/javascript'):
            return True
    return False


def find_precision(value):
    """Find precision of some arbitrary value.

    The main intention for this function is to use it together with
    turbogears.i18n.format.format_decimal() where one has to inform
    the precision wanted. So, use it like this:

    format_decimal(some_number, find_precision(some_number))

    """
    decimals = ''
    try:
        decimals = str(value).split('.', 1)[1]
    except IndexError:
        pass
    return len(decimals)


def copy_if_mutable(value, feedback=False):
    """Make a copy of the value if it is mutable.

    Returns the value. If feedback is set to true, also returns
    whether value was mutable as the second element of a tuple.

    """
    if isinstance(value, dict):
        mutable = True
        value = value.copy()
    elif isinstance(value, list):
        mutable = True
        value = value[:]
    else:
        mutable = False
    if feedback:
        return value, mutable
    else:
        return value


def fixentities(htmltext):
    """Replace HTML character entities with numerical references.

    Note: This won't handle CDATA sections properly.

    """
    def repl(matchobj):
        entity = htmlentitydefs.entitydefs.get(matchobj.group(1).lower())
        if not entity:
            return matchobj.group(0)
        elif len(entity) == 1:
            if entity in '&<>\'"':
                return matchobj.group(0)
            return '&#%d;' % ord(entity)
        else:
            return entity
    return re.sub('&(\w+);?', repl, htmltext)


if hasattr(socket, 'inet_pton') and hasattr(socket, 'AF_INET6'):

    def inet6_aton(addr):
        """Convert IP6 standard hex notation to IP6 address."""
        return socket.inet_pton(socket.AF_INET6, addr)

else: # Windows etc.

    import string
    _inet6_chars = string.hexdigits + ':.'

    def inet6_aton(addr):
        """Convert IPv6 standard hex notation to IPv6 address.

        Inspired by http://twistedmatrix.com/trac/.

        """
        faulty = addr.lstrip(_inet6_chars)
        if faulty:
            raise ValueError("Illegal character '%c' in IPv6 address" % faulty[0])
        parts = addr.split(':')
        elided = parts.count('')
        extenso = '.' in parts[-1] and 7 or 8
        if len(parts) > extenso or elided > 3:
            raise ValueError("Syntactically invalid IPv6 address")
        if elided == 3:
            return '\x00' * 16
        if elided:
            zeros = ['0'] * (extenso - len(parts) + elided)
            if addr.startswith('::'):
                parts[:2] = zeros
            elif addr.endswith('::'):
                parts[-2:] = zeros
            else:
                idx = parts.index('')
                parts[idx:idx+1] = zeros
        if len(parts) != extenso:
            raise ValueError("Syntactically invalid IPv6 address")
        if extenso == 7:
            ipv4 = parts.pop()
            if ipv4.count('.') != 3:
                raise ValueError("Syntactically invalid IPv6 address")
            parts = [int(x, 16) for x in parts]
            return struct.pack('!6H', *parts) + socket.inet_aton(ipv4)
        else:
            parts = [int(x, 16) for x in parts]
            return struct.pack('!8H', *parts)


def inet_aton(addr):
    """Convert IPv4 or IPv6 notation to IPv6 address."""
    if ':' in addr:
        return inet6_aton(addr)
    else:
        return struct.pack('!QL', 0, 0xffff) + socket.inet_aton(addr)


def _inet_prefix(addr, masked):
    """Remove the number of masked bits from the IPV6 address."""
    hi, lo = struct.unpack("!QQ", addr)
    return (hi << 64 | lo) >> masked


def match_ip(cidr, ip):
    """Check whether IP address matches CIDR IP address block."""
    if '/' in cidr:
        cidr, prefix = cidr.split('/', 1)
        masked = (':' in cidr and 128 or 32) - int(prefix)
    else:
        masked = None
    cidr = inet_aton(cidr)
    ip = inet_aton(ip)
    if masked:
        cidr = _inet_prefix(cidr, masked)
        ip = _inet_prefix(ip, masked)
    return ip == cidr

