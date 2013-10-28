"""The PEAK Rules Framework"""

from peak.rules.core import abstract, when, before, after, around, istype, \
    DispatchError, AmbiguousMethods, NoApplicableMethods, value

def combine_using(*wrappers):
    """Designate a generic function that wraps the iteration of its methods

    Standard "when" methods will be combined by iteration in precedence order,
    and the resulting iterator will be passed to the supplied wrapper(s), last
    first.  (e.g. ``combine_using(sorted, itertools.chain)`` will chain the
    sequences supplied by each method into one giant list, and then sort it).

    As a special case, if you include ``abstract`` in the wrapper list, it
    will be removed, and the decorated function will be marked as abstract.

    This decorator can only be used once per function, and can't be used if
    the generic function already has methods (even the default method) or if
    a custom method type has already been set (e.g. if you already called
    ``combine_using()`` on it before).
    """
    is_abstract = abstract in wrappers
    if is_abstract:
        wrappers = tuple([w for w in wrappers if w is not abstract])
        
    def callback(frame, name, func, old_locals):
        if core.Dispatching.exists_for(func) and list(core.rules_for(func)):
            raise RuntimeError("Methods already defined for", func)
        if is_abstract:
            func = abstract(func)
        r = core.Dispatching(func).rules
        if r.default_actiontype is not core.Method:
            raise RuntimeError("Method type already defined for", func)
        r.default_actiontype = core.MethodList.make
        r.methodlist_wrappers = wrappers[::-1]
        if not is_abstract:
            r.add(core.Rule(core.clone_function(func)))
        return func
    return core.decorate_assignment(callback)


def expand_as(predicate_string):
    """In rules, use the supplied condition in place of the decorated function

    Usage::
        @expand_as('filter is None or value==filter')
        def check(filter, value):
            "Check whether value matches filter"

    When the above function is used in a rule, the supplied condition will
    be "inlined", so that PEAK-Rules can expand the function call without
    losing its ability to index the rule or determine its precedence relative
    to other rules.

    When the condition is inlined, it's done in a namespace-safe manner.
    Names in the supplied condition will refer to either the arguments of the
    decorated function, or to locals/globals in the frame where ``expand_as``
    was called.  Names defined in the condition body (e.g. via ``let``) will
    not be visible to the caller.

    To prevent needless code duplication, you do not need to provide a body for
    your function, unless it is to behave differently than the supplied
    condition when it's called outside a rule.  If the decorated function has
    no body of its own (i.e. it's a ``pass`` or just a docstring), the supplied
    condition will be compiled to provide one automatically.  (That's why the
    above example usage has no body for the ``check()`` function.)
    """    
    def callback(frame, name, func, old_locals):
        from peak.rules.predicates import _expand_as
        kind, module, locals_, globals_ = core.frameinfo(frame)
        return _expand_as(
            func, predicate_string, locals_, globals_, __builtins__
        )
    return core.decorate_assignment(callback)








def let(**kw):
    """Define temporary variables for use in rules and methods

    Usage::

        @when(somefunc, "let(x=foo(y), z=y*2) and x>z")
        def some_method((x,z), next_method, y):
            # do something here

    The keywords used in the let() expression become available for use in
    any part of the rule that is joined to the ``let()`` by an ``and``
    expression, but will not be available in expressions joined by ``or`` or
    ``not`` branches.  Any ``let()`` calls at the top level of the expression
    will also be available for use in the method body, if you place them in
    a tuple argument in the *very first* argument position -- even before
    ``next_method`` and ``self``.

    Note that variables defined by ``let()`` are **lazy** - their values are
    not computed until/unless they are actually needed by the relevant part
    of the rule, so it does not slow things down at runtime to list all your
    variables up front.  Likewise, only the variables actually listed in your
    first-argument tuple are calculated, and only when the method is actually
    invoked.

    (Currently, this feature is mainly to support easy-to-understand rules,
    and DRY method bodies, as variables used in the rule's criteria may be
    calculated a second time when the method is invoked.)

    Note that while variable calculation is lazy, there *is* an evaluation
    order *between* variables in a let; you can't use a let-variable before
    it's been defined; you'll instead get whatever argument, local, or global
    variable would be shadowed by the as-yet-undefined variable.
    """
    raise NotImplementedError("`let` can only be used in rules, not code!")

__all__ = [_k for _k in list(globals()) if not _k.startswith('_') and _k!='core']
# TEMPORARY BACKWARDS COMPATIBILITY - PLEASE IMPORT THIS DIRECTLY FROM CORE
# (or better still, use the '>>' operator that method types now have)
#
from peak.rules.core import *  # always_overrides, Method, etc.

