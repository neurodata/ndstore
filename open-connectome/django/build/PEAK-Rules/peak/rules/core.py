__all__ = [
    'Rule', 'RuleSet', 'Dispatching', 'Engine', 'rules_for', 'compile_method',
    'Method', 'Around', 'Before', 'After', 'MethodList', 'value',
    'DispatchError', 'AmbiguousMethods', 'NoApplicableMethods',
    'abstract', 'when', 'before', 'after', 'around', 'istype', 'parse_rule',
    'implies', 'dominant_signatures', 'combine_actions', 'overrides',
    'always_overrides', 'merge_by_default', 'intersect', 'disjuncts', 'negate'
]
from peak.util.decorators import decorate_assignment, decorate, struct, \
            synchronized, frameinfo, decorate_class, classy, apply_template
from peak.util.assembler import Code, Const, Call, Local, Getattr, TryExcept, \
            Suite, with_name
from peak.util.addons import AddOn
import inspect, new, itertools, operator, sys
try:
    set, frozenset = set, frozenset
except NameError:
    from sets import Set as set
    from sets import ImmutableSet
    class frozenset(ImmutableSet):
        """Kludge to fix the abomination that is ImmutableSet.__init__"""
        def __new__(cls, iterable=None):
            self = ImmutableSet.__new__(cls, iterable)
            ImmutableSet.__init__(self, iterable)
            return self
        def __init__(self, iterable=None):
            pass    # all immutable initialization should be done by __new__!
empty = frozenset()
try:
    sorted = sorted
except NameError:
    def sorted(seq,key=None):
        if key:
            d = [(key(v),v) for v in seq]
        else:
            d = list(seq)
        d.sort()
        if key:
            return [v[1] for v in d]
        return d

# Core logic -- many of these are generics to be specialized w/"when" later

def disjuncts(ob):
    """Return a *list* of the logical disjunctions of `ob`"""
    # False == no condition is sufficient == no disjuncts
    if ob is False: return []
    if type(ob) is tuple: return _tuple_disjuncts(ob)
    return [ob]

def implies(s1,s2):
    """Is s2 always true if s1 is true?"""
    return s1==s2

def overrides(a1, a2):
    """Does action a1 take precedence over action a2?"""
    return False

def combine_actions(a1,a2):
    """Return a new action for the combination of a1 and a2"""
    if a1 is None:
        return a2
    elif a2 is None:
        return a1
    elif overrides(a1,a2):
        if not overrides(a2,a1):
            return a1.override(a2)
    elif overrides(a2,a1):
        return a2.override(a1)
    return a1.merge(a2)

def rules_for(f):
    """Return the initialized ruleset for a generic function"""
    if not Dispatching.exists_for(f):
        d = Dispatching(f)
        d.rules.add(Rule(clone_function(f)))
    return Dispatching(f).rules





class Dispatching(AddOn):
    """Manage a generic function's rules, engine, locking, and code"""
    engine = None
    def __init__(self, func):
        func.__doc__    # workaround for PyPy issue #1293
        self.function = func
        self._regen   = self._regen_code()  # callback to regenerate code
        self.rules    = RuleSet(self.get_lock())
        self.backup   = None  # allows func to call itself during regeneration
        self.create_engine(TypeEngine)

    synchronized()
    def get_lock(self):
        return self.__lock__

    def create_engine(self, engine_type):
        """Create a new engine of `engine_type`, unsubscribing old"""
        if self.engine is not None and self.engine in self.rules.listeners:
            self.rules.unsubscribe(self.engine)
        self.engine = engine_type(self)
        return self.engine

    synchronized()
    def request_regeneration(self):
        """Ensure code regeneration occurs on next call of the function"""
        if self.backup is None:
            self.backup = self.function.func_code
            self.function.func_code = self._regen
    def _regen_code(self):
        c = Code.from_function(self.function, copy_lineno=True)
        c.return_(
            call_thru(
                self.function,
                Call(Getattr(
                    Call(Const(Dispatching), (Const(self.function),), fold=False),
                    '_regenerate'
                ))
            )
        )
        return c.code()

    synchronized()
    def as_abstract(self):
        for action in self.rules:
            raise AssertionError("Can't make abstract: rules already exist")

        c = Code.from_function(self.function, copy_lineno=True)
        c.return_(call_thru(self.function, Const(self.rules.default_action)))

        if self.backup is None:
            self.function.func_code = c.code()
        else:
            self.backup = c.code()
        return self.function

    synchronized()
    def _regenerate(self):
        func = self.function
        assert self.backup is not None
        func.func_code = self.backup    # ensure re-entrant calls work

        try:
            # try to replace the code with new code
            func.func_code = self.engine._generate_code()
        except:
            # failure: we'll try to regen again, next time we're called
            func.func_code = self._regen
            raise
        else:
            # success!  get rid of the old backup code and return the function
            self.backup = None
            return func










class DispatchError(Exception):
    """A dispatch error has occurred"""

    def __call__(self,*args,**kw):
        raise self.__class__(*self.args+(args,kw))  # XXX

    def __repr__(self):
        # This method is needed so doctests for 2.3/2.4 match 2.5
        return self.__class__.__name__+repr(self.args)


class MethodType(type):
    """Metaclass for method types

    This allows precedence to be declared between method types, and ensures
    that ``compiled()`` methods aren't inherited when ``__call__`` is redefined
    in a Method subclass.
    """

    def __init__(cls, name, bases, cdict):
        if '__call__' in cdict and 'compiled' not in cdict:
            # Ensure 'compiled()' is not inherited for changed __call__
            cls.compiled = lambda self, engine: self
        return type.__init__(cls, name, bases, cdict)

    def __rshift__(self, other):
        if type(other) is tuple:
            for item in other:
                always_overrides(self, item)
        else:
            always_overrides(self, other)
        return other

    def __rrshift__(self, other):
        if type(other) is tuple:
            for item in other:
                always_overrides(item, self)
        else:
            always_overrides(other, self)
        return self

class Method(object):
    """A simple method w/optional chaining"""

    __metaclass__ = MethodType
    
    def __init__(self, body, signature=(), serial=0, tail=None):
        self.body = body
        self.signature = signature
        self.serial = serial
        self.tail = tail
        self.can_tail = False
        try:
            args = inspect.getargspec(body)[0]
        except TypeError:
            pass
        else:
            if args and args[0]=='next_method':
                if getattr(body, 'im_self', None) is None:  # already bound?
                    self.can_tail = True

    decorate(classmethod)
    def make(cls, body, signature=(), serial=0):
        return cls(body, signature, serial)

    def __repr__(self):
        data = (self.body, self.signature, self.serial, self.tail)
        return self.__class__.__name__+repr(data)

    def __call__(self, *args, **kw):
        """Slow way to call a method -- use compile_method instead!"""
        return compile_method(self)(*args, **kw)
        
    def override(self, other):
        if not self.can_tail:
            return self
        return self.tail_with(combine_actions(self.tail, other))

    def tail_with(self, tail):
        return self.__class__(self.body, self.signature, self.serial, tail)


    def merge(self, other):
        #if self.__class__ is other.__class__ and self.body is other.body:
        #    XXX need to merge signatures?
        #    return self.__class__(
        #        self.body, ???, ???, combine_actions(self.tail, other.tail)
        #    )
        return AmbiguousMethods([self,other])

    decorate(classmethod)
    def make_decorator(cls, name, doc=None):
        if doc is None:
            doc = "Extend a generic function with a method of type ``%s``" \
                  % cls.__name__
        if cls is Method:
            maker = None   # allow gf's to use something else instead of Method
        else:
            maker = cls.make
        def decorate(f, pred=(), depth=2, frame=None):
            def callback(frame, name, func, old_locals):
                assert f is not func    # XXX
                kind, module, locals_, globals_ = frameinfo(frame)
                context = ParseContext(func, maker, locals_, globals_, lineno)
                def register_for_class(cls, f=f):
                    _register_rule(f, pred, context, cls)
                    return cls
                if kind=='class':
                    # 'when()' in class body; defer adding the method
                    decorate_class(register_for_class, frame=frame)
                else:
                    register_for_class(None)
                if old_locals.get(name) is f:
                    return f    # prevent overwriting if name is the same
                return func
            rv = decorate_assignment(callback, depth, frame)
            if frame is None: frame = sys._getframe(depth-1)
            lineno = frame.f_lineno # this isn't valid w/out active trace!
            return rv
        decorate = with_name(decorate, name)
        decorate.__doc__ = doc
        return decorate

    def compiled(self, engine):
        body = compile_method(self.body, engine)
        if not self.can_tail:
            return body
        else:
            return new.instancemethod(body, compile_method(self.tail, engine))

when = Method.make_decorator(
    "when", "Extend a generic function with a new action"
)


class NoApplicableMethods(DispatchError):
    """No applicable action has been defined for the given arguments"""

    def merge(self, other):
        return AmbiguousMethods([self,other])


class AmbiguousMethods(DispatchError):
    """More than one choice of action is possible"""

    def __init__(self, methods, *args):
        DispatchError.__init__(self, methods, *args)
        mine = self.methods = []
        for m in methods:
            if isinstance(m, AmbiguousMethods):
                mine.extend(m.methods)
            else:
                mine.append(m)

    def merge(self, other):
        return AmbiguousMethods(self.methods+[other])

    def override(self, other):
        return self

    def __repr__(self):
        return "AmbiguousMethods(%s)" % self.methods


class RuleSet(object):
    """An observable, stably-ordered collection of rules"""
    default_action = NoApplicableMethods()
    default_actiontype = Method

    def __init__(self, lock=None):
        self.rules = []
        self.actiondefs = {}
        self.listeners = []
        if lock is not None:
            self.__lock__ = lock

    synchronized()
    def add(self, rule):
        actiondefs = frozenset(self._actions_for(rule))
        self.rules.append( rule )
        self.actiondefs[rule] = actiondefs
        self._notify(added=actiondefs)

    synchronized()
    def remove(self, rule):
        actiondefs = self.actiondefs.pop(rule)
        self.rules.remove(rule)
        self._notify(removed=actiondefs)

    #def changed(self, rule):
    #    sequence, actions = self.actions[rule]
    #    new_actions = frozenset(self._actions_for(rule, sequence))
    #    self.actions[rule] = sequence, new_actions
    #    self.notify(new_actions-actions, actions-new_actions)

    synchronized()
    def clear(self):
        actiondefs = frozenset(self)
        del self.rules[:]; self.actiondefs.clear()
        self._notify(removed=actiondefs)

    def _notify(self, added=empty, removed=empty):
        for listener in self.listeners[:]:  # must be re-entrant
            listener.actions_changed(added, removed)

    synchronized()
    def __iter__(self):
        ad = self.actiondefs
        return iter([a for rule in self.rules for a in ad[rule]])

    def _actions_for(self, (na, body, predicate, actiontype, seq)):
        actiontype = actiontype or self.default_actiontype
        for signature in disjuncts(predicate):
            yield Rule(body, signature, actiontype, seq)

    synchronized()
    def subscribe(self, listener):
        self.listeners.append(listener)
        if self.rules:
            listener.actions_changed(frozenset(self), empty)

    synchronized()
    def unsubscribe(self, listener):
        self.listeners.remove(listener)


def _register_rule(gf, pred, context, cls):
    """Register a rule for `gf` with possible import-deferring"""
    if not isinstance(gf, basestring):
        rules = rules_for(gf)
        rules.add(parse_rule(Dispatching(gf).engine, pred, context, cls))
        return
    if len(gf.split(':'))<>2 or len(gf.split())>1:
        raise TypeError(
            "Function specifier %r is not in 'module.name:attrib.name' format"
            % (gf,)
        )
    modname, attrname = gf.split(':')
    from peak.util.imports import whenImported
    def _delayed_register(module):
        for attr in attrname.split('.'):
            module = getattr(module, attr)
        _register_rule(module, pred, context, cls)
    whenImported(modname, _delayed_register)


class Engine(object):
    """Abstract base for dispatching engines"""

    reset_on_remove = True

    def __init__(self, disp):
        self.function = disp.function
        self.registry = {}
        self.closures = {}
        self.rules = disp.rules
        self.__lock__ = disp.get_lock()
        self.argnames = list(
            flatten(filter(None, inspect.getargspec(self.function)[:3]))
        )
        self.rules.subscribe(self)

    synchronized()
    def actions_changed(self, added, removed):
        if removed and self.reset_on_remove:
            return self._full_reset()
        for rule in removed:
            self._remove_method(rule.predicate, rule)
        for rule in added:
            self._add_method(rule.predicate, rule)
        if added or removed:
            self._changed()

    def _changed(self):
        """Some change to the rules has occurred"""
        Dispatching(self.function).request_regeneration()

    def _full_reset(self):
        """Regenerate any code, caches, indexes, etc."""
        self.registry.clear()
        self.actions_changed(self.rules, ())
        Dispatching(self.function).request_regeneration()





    compiled_cache = None

    def apply_template(self, template, *args):
        try:
            return self.compiled_cache[template, args]
        except (KeyError, TypeError, AttributeError):
            pass

        try:
            closure = self.closures[template]
        except KeyError:
            if template.func_closure:
                raise TypeError("Templates cannot use outer-scope variables")
            import linecache; from peak.util.decorators import cache_source
            tmp = apply_template(template, self.function, *args)
            body = ''.join(linecache.getlines(tmp.func_code.co_filename))
            filename = "<%s at 0x%08X wrapping %s at 0x%08X>" % (
                template.__name__, id(template),
                self.function.__name__, id(self)
            )
            d ={}
            exec compile(body, filename, "exec") in template.func_globals, d
            tmp, closure = d.popitem()
            closure.func_defaults = template.func_defaults
            cache_source(filename, body, closure)
            self.closures[template] = closure
        f = closure(self.function, *args)
        f.func_defaults = self.function.func_defaults

        try:
            hash(args)
        except TypeError:
            pass
        else:
            if self.compiled_cache is None:
                from weakref import WeakValueDictionary
                self.compiled_cache = WeakValueDictionary()
            self.compiled_cache[template, args] = f
        return f


    def _add_method(self, signature, rule):
        """Add a case for the given signature and rule"""
        registry = self.registry
        action = rule.actiontype(rule.body, signature, rule.sequence)
        if signature in registry:
            registry[signature] = combine_actions(registry[signature], action)
        else:
            registry[signature] = action
        return action

    def _remove_method(self, signature, rule):
        """Remove the case for the given signature and rule"""
        raise NotImplementedError

    def _generate_code(self):
        """Return a code object for the current state of the function"""
        raise NotImplementedError
























class TypeEngine(Engine):
    """Simple type-based dispatching"""

    cache = None

    def __init__(self, disp):
        self.static_cache = {}
        super(TypeEngine, self).__init__(disp)

    def _changed(self):
        if self.cache != self.static_cache:
            Dispatching(self.function).request_regeneration()

    def _bootstrap(self):
        # Bootstrap a self-referential generic function by ensuring an exact
        # list of signatures is always in the function's dispatch cache.
        #
        # Only peak.rules.core generic functions used in the implementation of
        # other generic functions need this; currently that's just implies()
        # and overrides(), which control method order and combining.
        #
        cache = self.static_cache
        for sig, act in self.registry.items():
            for key in type_keys(sig):
                cache[key] = compile_method(act, self)
        self._changed()

    def _add_method(self, signature, rule):
        action = super(TypeEngine, self)._add_method(signature, rule)
        cache = self.static_cache
        for key in cache.keys():
            if key==signature or implies(key, signature):
                del cache[key]
        return action







    def _generate_code(self):
        self.cache = cache = self.static_cache.copy()
        def callback(*args, **kw):
            types = tuple([getattr(arg,'__class__',type(arg)) for arg in args])
            key = tuple(map(istype, types))
            self.__lock__.acquire()
            try:
                action = self.rules.default_action
                for sig in self.registry:
                    if implies(key, sig):
                        action = combine_actions(action, self.registry[sig])
                f = cache[types] = compile_method(action, self)
            finally:
                self.__lock__.release()
            return f(*args, **kw)

        c = Code.from_function(self.function, copy_lineno=True)
        types = [class_or_type_of(Local(name))
                    for name in flatten(inspect.getargspec(self.function)[0])]
        target = Call(Const(cache.get), (tuple(types), Const(callback)))
        c.return_(call_thru(self.function, target))
        return c.code()


# Handle alternates in tuple signatures
#
# when(disjuncts, (istype(tuple),)) - this has to be hardcoded for bootstrap
def _tuple_disjuncts(ob):
    for posn, item in enumerate(ob):
        if type(item) is tuple:
            head = ob[:posn]
            return [
                head+(mid,)+tail
                    for tail in _tuple_disjuncts(ob[posn+1:]) for mid in item
            ]
    return [ob]     # no alternates





# Code generation stuff

def flatten(v):
    if isinstance(v,basestring): yield v; return
    for i in v:
        for ii in flatten(i): yield ii

def gen_arg(v):
    if isinstance(v,basestring): return Local(v)
    if isinstance(v,list): return tuple(map(gen_arg,v))

def call_thru(sigfunc, target, prefix=()):
    args, star, dstar, defaults = inspect.getargspec(sigfunc)
    return Call(target, list(prefix)+map(gen_arg,args), (), gen_arg(star), gen_arg(dstar), fold=False)

def class_or_type_of(expr):
    return Suite([expr, TryExcept(
        Suite([Getattr(Code.DUP_TOP, '__class__'), Code.ROT_TWO, Code.POP_TOP]),
        [(Const(AttributeError), Call(Const(type), (Code.ROT_TWO,)))]
    )])

def clone_function(f):
    return new.function(
      f.func_code, f.func_globals, f.func_name, f.func_defaults, f.func_closure
    )

_default_engine = None
def compile_method(action, engine=None):
    """Convert `action` into an optimized callable for `engine`"""
    if engine is None:
        global _default_engine
        if _default_engine is None:
            _default_engine = Dispatching(abstract(lambda *a, **k: None)).engine
        # allow any rules on non-None engines to apply
        return compile_method(action, _default_engine)
    if isinstance(action, (Method, value)):
        return action.compiled(engine)
    elif action is None:
        return engine.rules.default_action
    return action

# Rules management

def abstract(func=None):
    """Declare a function to be abstract"""
    if func is None:
        return decorate_assignment(
            lambda f,n,func,old: Dispatching(func).as_abstract()
        )
    else:
        return Dispatching(func).as_abstract()

next_sequence = itertools.count().next

struct()
def Rule(body, predicate=(), actiontype=None, sequence=None):
    if sequence is None:
        sequence = next_sequence()
    return body, predicate, actiontype, sequence

struct()
def ParseContext(
    body, actiontype=None, localdict=(), globaldict=(), lineno=None, sequence=None
):
    """Hold information needed to parse a predicate"""
    if sequence is None:
        sequence = next_sequence()
    return body, actiontype, dict(localdict), dict(globaldict), lineno, sequence

def parse_rule(engine, predicate, context, cls):
    """Hook for pre-processing predicates, e.g. parsing string expressions"""
    if cls is not None and type(predicate) is tuple:
        predicate = (cls,) + predicate        
    return Rule(context.body, predicate, context.actiontype, context.sequence)








# Class/type rules and implications

[struct()]
def istype(type, match=True):
    return type, match

def type_key(arg):
    if isinstance(arg, (type, ClassType)):
        return arg
    elif type(arg) is istype and arg.match:
        return arg.type

def type_keys(sig):
    if type(sig) is tuple:
        key = tuple(map(type_key, sig))
        if None not in key:
            yield key

when(implies, (istype(tuple), istype(tuple)))
def tuple_implies(s1,s2):
    if len(s2)>len(s1):
        return False    # shorter tuple can't imply longer tuple
    for t1,t2 in zip(s1,s2):
        if not implies(t1,t2):
            return False
    else:
        return True

from types import ClassType, InstanceType
when(implies, (type,      (ClassType, type) ))(issubclass)
when(implies, (ClassType,  ClassType        ))(issubclass)
when(implies, (istype,     istype           ))(lambda s1,s2:
    s1==s2 or (s1.type is not s2.type and s1.match and not s2.match))
when(implies, (istype,    (ClassType, type) ))(lambda s1,s2:
    s1.match and implies(s1.type,s2))

# A classic class only implies a new-style one if it's ``object``
# or ``InstanceType``; this is an exception to the general rule that
# isinstance(X,Y) implies issubclass(X.__class__,Y)
when(implies, (ClassType, type))(lambda s1,s2: s2 is object or s2 is InstanceType)

# Rule precedence

[struct(
    __call__ = lambda self,*a,**kw: self.value,
    compiled = lambda self, engine:
                      engine.apply_template(value_template, self.value),
    __repr__ = lambda self: 'value(%r)' % self[1:]
)]
def value(value):
    """Method body returning a constant value"""
    return value,

def value_template(__func,__value):
    return "return __value"

YES, NO = value(True), value(False)

def always_overrides(a, b):
    """`a` instances always override `b`s; `b` instances never override `a`s"""
    a,b = istype(a), istype(b)
    pairs = {}
    to_add = [(a,b)]
    for rule in rules_for(overrides):
        sig = rule.predicate
        if type(sig) is not tuple or len(sig)!=2 or rule.body is not YES:
            continue
        pairs[sig]=1
        if sig[0]==b: to_add.append((a, sig[1]))
        if sig[1]==a: to_add.append((sig[0], b))
    for (p1,p2) in to_add:
        if (p2,p1) in pairs:
            raise TypeError("%r already overrides %r" % (b.type, a.type))
    for (p1,p2) in to_add:
        if (p1,p2) not in pairs:
            when(overrides, (p1, p2))(YES)
            when(overrides, (p2, p1))(NO)

def merge_by_default(t):
    """instances of `t` never imply other instances of `t`"""
    when(overrides, (t, t))(NO)

class MethodList(Method):
    """A list of related methods"""

    can_tail = False
    _sorted_items = None

    def __init__(self, items=(), tail=None):
        self.items = list(items)
        self.tail = tail

    decorate(classmethod)
    def make(cls, body, signature=(), serial=0):
        return cls( [(serial, signature, body)] )

    def __repr__(self):
        data = self.items, self.tail
        return self.__class__.__name__+repr(data)

    def tail_with(self, tail):
        return self.__class__(self.items, tail)

    def merge(self, other):
        if other.__class__ is not self.__class__:
            raise TypeError("Incompatible action types for merge", self, other)
        return self.__class__(
            self.items+other.items, combine_actions(self.tail, other.tail)
        )

    def compiled(self, engine):
        wrappers = tuple(engine.rules.methodlist_wrappers)
        bodies = [compile_method(body,engine) for sig, body in self.sorted()]
        return engine.apply_template(list_template, tuple(bodies), wrappers)









    def sorted(self):
        if self._sorted_items is not None:
            return self._sorted_items

        self.items.sort()
        rest = [(s,b) for (serial, s, b) in self.items]

        self._sorted_items = items = []
        seen = set()
        while rest:
            best = dominant_signatures(rest)
            map(rest.remove, best)
            for s,b in best:
                if b not in seen:
                    seen.add(b)
                    items.append((s,b))
        return items

def list_template(__func, __bodies, __wrappers):
    return """
    def __iterate():
        for __body in __bodies: yield __body($args)
    __result = __iterate()
    for __wrapper in __wrappers:
        __result = __wrapper(__result)
    return __result"""

merge_by_default(MethodList)


class Around(Method):
    """'Around' Method (takes precedence over regular methods)"""

around = Around.make_decorator('around')







class Before(MethodList):
    """Method(s) to be called before the primary method(s)"""
    can_tail = True

    def compiled(self, engine):
        tail = compile_method(self.tail, engine)
        bodies = [compile_method(body,engine) for sig, body in self.sorted()]
        return engine.apply_template(before_template, tail, tuple(bodies))

def before_template(__func, __tail, __bodies):
    return """
    for __body in __bodies: __body($args)
    return __tail($args)"""
    
before = Before.make_decorator('before')

class After(MethodList):
    """Method(s) to be called after the primary method(s)"""
    can_tail = True

    def sorted(self):
        # Reverse the sorting for after methods
        if self._sorted_items is not None:
            return self._sorted_items
        items = super(After,self).sorted()
        items.reverse()
        return items

    def compiled(self, engine):
        tail = compile_method(self.tail, engine)
        bodies = [compile_method(body, engine) for sig, body in self.sorted()]
        return engine.apply_template(after_template, tail, tuple(bodies))

def after_template(__func, __tail, __bodies):
    return """
    __retval = __tail($args)
    for __body in __bodies: __body($args)
    return __retval"""

after  = After.make_decorator('after')

# Define the overall method order
Around >> Before >> After >> (Method, MethodList)

# These are necessary to ensure that any added Method subclasses will
# automatically override NoApplicableMethods (and any subclasses thereof):
#
when(overrides, (Method, NoApplicableMethods))(YES)
when(overrides, (NoApplicableMethods, Method))(NO)

when(overrides, (Method,Method))
def method_overrides(a1, a2):
    if a1.__class__ is a2.__class__:
        return implies(a1.signature, a2.signature)
    raise TypeError("Incompatible action types", a1, a2)

when(overrides, (AmbiguousMethods, Method))
def ambiguous_overrides(a1, a2):
    for m in a1.methods:
        if overrides(m, a2):
            # if any ambiguous method overrides a2, we can toss it
            return True
    return False

when(overrides, (Method, AmbiguousMethods))
def override_ambiguous(a1, a2):
    for m in a2.methods:
        if not overrides(a1, m):
            return False
    return True     # can only override if it overrides all the ambiguity

# needed to disambiguate the above two methods if combining a pair of AM's:
merge_by_default(AmbiguousMethods)

# And now we can bootstrap the core!  These two functions are used in the
# TypeEngine implementation, so we force them to statically cache all their
# current methods.  That way, they'll still work even if they're called during
# one of their own cache misses or code regenerations:
Dispatching(implies).engine._bootstrap()
Dispatching(overrides).engine._bootstrap()


when(parse_rule, (TypeEngine, istype(tuple, False)))
def parse_upgrade(engine, predicate, context, cls):
    """Upgrade to predicate dispatch engine when called w/unrecognized args"""
    if isinstance(predicate, (type, ClassType, istype)):
        # convert single item to tuple - no need to upgrade engine
        return parse_rule(engine, (predicate,), context, cls)
    from peak.rules.predicates import IndexedEngine
    return parse_rule(
        Dispatching(engine.function).create_engine(IndexedEngine),
        predicate, context, cls
    )

when(rules_for, type(After.sorted))(lambda f: rules_for(f.im_func))


# Logical functions needed for extensions to the core, but that should be
# shared by all extensions.

abstract()
def negate(c):
    """Return the logical negation of criterion `c`"""

when(negate, (bool,)  )(operator.not_)
when(negate, (istype,))(lambda c: istype(c.type, not c.match))

abstract()
def intersect(c1, c2):
    """Return the logical intersection of two conditions"""

around(intersect, (object, object))
def intersect_if_implies(next_method, c1, c2):
    if implies(c1,c2):      return c1
    elif implies(c2, c1):   return c2
    return next_method(c1, c2)

# These are needed for boolean intersects to work correctly
when(implies, (bool, bool))(lambda c1, c2: c2 or not c1)
when(implies, (bool, object))(lambda c1, c2: not c1)
when(implies, (object, bool))(lambda c1, c2: c2)


def dominant_signatures(cases):
    """Return the most-specific ``(signature,body)`` pairs from `cases`

    `cases` is a sequence of ``(signature,body)`` pairs.  This routine checks
    the ``implies()`` relationships between pairs of signatures, and then
    returns a list of ``(signature,method)`` pairs such that no signature
    remaining in the original list implies a signature in the new list.
    The relative order of cases in the new list is preserved.
    """

    if len(cases)==1:
        # Shortcut for common case
        return list(cases)

    best, rest = list(cases[:1]), list(cases[1:])

    for new_sig, new_meth in rest:

        for old_sig, old_meth in best[:]:   # copy so we can modify inplace

            new_implies_old = implies(new_sig, old_sig)
            old_implies_new = implies(old_sig, new_sig)

            if new_implies_old:

                if not old_implies_new:
                    # better, remove the old one
                    best.remove((old_sig, old_meth))

            elif old_implies_new:
                # worse, skip adding the new one
                break
        else:
            # new_sig has passed the gauntlet, as it has not been implied
            # by any of the current "best" items
            best.append((new_sig,new_meth))

    return best



