"""Decorator tools"""

__all__ = ['decorate', 'make_weak_signature', 'compose',
    'decorator', 'weak_signature_decorator',
    'simple_decorator', 'simple_weak_signature_decorator',
    'func_id', 'func_eq', 'func_original', 'func_composition']

import itertools
from inspect import getargspec, formatargspec


def decorate(func, caller, signature=None):
    """Decorate func with caller.

    Inspired by Michele Simionato's decorator library:
    http://www.phyast.pitt.edu/~micheles/python/documentation.html

    """
    argnames, varargs, kwargs, defaults = \
        signature is None and getargspec(func) or signature
    if defaults is None:
        defaults = ()
    parameters = formatargspec(argnames, varargs, kwargs, defaults)[1:-1]
    defval = itertools.count(len(argnames) - len(defaults))
    args = formatargspec(argnames, varargs, kwargs, defaults,
        formatvalue=lambda value:"=%s" % argnames[defval.next()])[1:-1]
    exec_dict = dict(func=func, caller=caller)
    exec "\ndef %s(%s):\n\treturn caller(func, %s)\n" % (
        func.__name__, parameters, args) in exec_dict
    new_func = exec_dict[func.__name__]
    new_func.__doc__ = func.__doc__
    new_func.__dict__ = func.__dict__.copy()
    new_func.__module__ = func.__module__
    new_func.__composition__ = getattr(func, '__composition__',
        [func]) + [new_func]
    return new_func


def decorator(entangler, signature=None):
    """Decorate function with entangler.

    Use new signature or preserve original signature if signature is None.

    """
    def entangle(func):
        return decorate(func, entangler(func), signature)
    return entangle


def weak_signature_decorator(entangler):
    """Decorate function with entangler and weak signature.

    Changes signature to accept arbitrary additional arguments.

    """
    def entangle(func):
        return decorate(func, entangler(func), make_weak_signature(func))
    return entangle


def simple_decorator(caller, signature=None):
    """Decorate function with caller."""
    def entangle(func):
        return decorate(func, caller, signature)
    return entangle


def simple_weak_signature_decorator(caller):
    """Decorate function with caller and weak signature.

    Changes signature to accept arbitrary additional arguments.

    """
    def entangle(func):
        return decorate(func, caller, make_weak_signature(func))
    return entangle


def make_weak_signature(func):
    """Change signature to accept arbitrary additional arguments."""
    argnames, varargs, kwargs, defaults = getargspec(func)
    if kwargs is None:
        kwargs = "_decorator__kwargs"
    if varargs is None:
        varargs = "_decorator__varargs"
    return argnames, varargs, kwargs, defaults


def compose(*decorators):
    """Compose decorators."""
    return lambda func: reduce(lambda f, g: g(f), decorators, func)


def func_composition(func):
    """Return composition (decorator wise) of function."""
    return getattr(func, "__composition__", [func])


def func_original(func):
    """Return original (undecorated) function."""
    return func_composition(func)[0]


def func_id(func):
    """Return identity of function.

    If decorator was created with decorator() or weak_signature_decorator(),
    identity is invariant under decorator application.

    """
    return id(func_original(func))


def func_eq(f, g):
    """Check if functions are identical."""
    return func_id(f) == func_id(g)

