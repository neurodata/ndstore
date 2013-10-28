"""RuleDispatch Emulation API"""
from peak.util.decorators import decorate_assignment
from peak.rules import core
from warnings import warn
import new, sys

__all__ = [
    'on', 'as', 'generic', 'as_'
]

def generic(combiner=None):
    """Please switch to using @peak.rules.abstract()"""
    if combiner is not None:
        raise AssertionError(
            "Custom combiners are not supported by the compatibility API;"
            " please use a custom method type instead"
        )
    def callback(frm,name,value,old_locals):
        value.when   = core.when.__get__(value)
        value.around = core.around.__get__(value)
        value.before = core.before.__get__(value)
        value.after  = core.after.__get__(value)
        def clear(): core.rules_for(value).clear()
        value.clear = clear
        return core.abstract(value)

    return decorate_assignment(callback)


def as_(*decorators):
    """Please switch to using @peak.util.decorators.decorate"""
    warn("Please use @peak.util.decorators.decorate instead of dispatch.as()",
        DeprecationWarning, 2
    )
    def callback(frame,k,v,old_locals):
        for d in decorators[::-1]: v = d(v)
        return v
    return decorate_assignment(callback)

globals()['as'] = as_  

def make_module():
    def callback(frm, name, value, old_locals):
        m = new.module('dispatch.'+name)
        v = value()
        m.__dict__.update(v)
        m.__all__ = list(v)
        sys.modules.setdefault(m.__name__, m)
        sys.modules.setdefault('peak.rules.'+m.__name__, m)        
        return m
    return decorate_assignment(callback)

make_module()
def interfaces():
    from peak.rules.core import DispatchError, NoApplicableMethods
    from peak.rules.core import AmbiguousMethods as AmbiguousMethod

    __all__.extend(locals())    # add these to the main namespace, too
    globals().update(locals())
    return locals()

make_module()
def strategy():
    default = ()
    from peak.util.extremes import Min, Max
    return locals()
















def on(argument_name):
    """Please switch to using @peak.rules.abstract()"""

    def callback(frm,name,value,old_locals):
        import inspect
        funcname = value.__name__
        args, varargs, kwargs, defaults = inspect.getargspec(value)
        if argument_name not in args:
            raise NameError("%r does not have an argument named %r"
                % (value, argument_name))
        argpos = args.index(argument_name)

        func = value

        def when(cond):
            """Add following function to this GF, using 'cond' as a guard"""
            def callback(frm,name,value,old_locals):
                core.when(func, (object,)*argpos + (cond,))(value)
                if old_locals.get(name) is func:
                    return func
                return value
            return decorate_assignment(callback)

        def clone():
            raise AssertionError("PEAK-Rules can't clone() generic functions")

        func.when = when
        func.clone = clone
        return core.abstract(func)

    return decorate_assignment(callback)


# Install
sys.modules.setdefault('dispatch', sys.modules[__name__])






