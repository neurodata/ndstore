from peak.util.assembler import *
from core import *
from core import class_or_type_of, call_thru, flatten
from criteria import *
from indexing import *
from codegen import SMIGenerator, ExprBuilder, Getitem, IfElse, Tuple
from peak.util.decorators import decorate, synchronized, decorate_assignment
from types import InstanceType, ClassType
from ast_builder import build, parse_expr
import inspect, new, codegen, parser

__all__ = [
    'IsInstance', 'IsSubclass', 'Truth', 'Identity', 'Comparison', 'priority',
    'IndexedEngine', 'predicate_node_for', 'meta_function', 'expressionSignature',
]

abstract()
def predicate_node_for(builder, expr, cases, remaining_exprs, memo):
    """Return a dispatch tree node argument appropriate for the expr"""

def value_check(val, (exact, ranges)):
    if val in exact:
        return exact[val]
    lo = 0
    hi = len(ranges)
    while lo<hi:
        mid = (lo+hi)//2
        (tl,th), node = ranges[mid]
        if val<tl:
            hi = mid
        elif val>th:
            lo = mid+1
        else:
            return node
    raise AssertionError("Should never get here")

nodetype()
def IsInstance(expr, code=None):
    if code is None: return expr,
    return IsSubclass(class_or_type_of(expr), code)

_unpack = lambda c: c.UNPACK_SEQUENCE(2)
subclass_check = TryExcept(
    Suite([
        Code.DUP_TOP, SMIGenerator.ARG, _unpack, Code.ROT_THREE,
        Code.POP_TOP, Code.BINARY_SUBSCR, Code.ROT_TWO, Code.POP_TOP
    ]), [(Const(KeyError), Suite([
        SMIGenerator.ARG, _unpack, Code.POP_TOP, Call(Code.ROT_TWO, (Pass,)),
    ]))]
)

nodetype()
def IsSubclass(expr, code=None):
    if code is None: return expr,
    code(expr, subclass_check)

identity_check = IfElse(
    Getitem(SMIGenerator.ARG, Code.ROT_TWO),
    Compare(Code.DUP_TOP, [('in', SMIGenerator.ARG)]),
    Suite([Code.POP_TOP, Getitem(SMIGenerator.ARG, None)])
)

nodetype()
def Identity(expr, code=None):
    if code is None: return expr,
    code(Call(Const(id), (expr,), fold=False), identity_check)

nodetype()
def Comparison(expr, code=None):
    if code is None: return expr,
    code.LOAD_CONST(value_check)
    Call(Pass, (expr, SMIGenerator.ARG), code=code)

nodetype()
def Truth(expr, code=None):
    if code is None: return expr,
    skip = Label()
    code(SMIGenerator.ARG); code.UNPACK_SEQUENCE(2)
    code(expr, skip.JUMP_IF_TRUE, Code.ROT_THREE, skip, Code.POP_TOP,
         Code.ROT_TWO, Code.POP_TOP)


class priority(int):
    """An integer priority for manually resolving a rule ambiguity"""
when(implies, (priority, priority))(lambda p1,p2: p1>=p2)

class ExprBuilder(ExprBuilder):
    """Extended expression builder with support for meta-functions"""

    def Backquote(self, expr):
        raise SyntaxError("backquotes are not allowed in predicates")

meta_functions = {}

def meta_function(*stub, **parsers):
    """Declare a meta-function and its argument parsers"""
    stub, = stub
    def callback(frame, name, func, old_locals):
        for name in inspect.getargs(func.func_code)[0]:
            if not isinstance(name, basestring):
                raise TypeError(
                    "Meta-functions cannot have packed-tuple arguments"
                )
        what = func, parsers, inspect.getargspec(func)
        meta_functions[stub] = (
            lambda builder, *args: apply_meta(builder, what, *args)
        )
        return func
    return decorate_assignment(callback)

def expressionSignature(expr):
    """Convert raw Python code into logical conditions"""
    # Default is to simply test the truth of the expression
    return Test(Truth(expr), Value(True))

when(expressionSignature, (Const,))(lambda expr: bool(expr.value))

when(expressionSignature, ((bool, Test, Signature, Disjunction),))
def pass_through(expr):
    return expr



class CriteriaBuilder(ExprBuilder):
    simplify_comparisons = True

    def build_with(self, expr):
        self.push()
        try:
            return build(self, expr)
        finally:
            self.pop()

    def Not(self, expr):
        return codegen.Not(self.build_with(expr))

    def Or(self, items):
        return codegen.Or(map(self.build_with, items))

    def CallFunc(self, func, args, kw, star_node, dstar_node):
        b = build.__get__(self)
        target = b(func)
        if isinstance(target, Const) and target.value in meta_functions:
            return meta_functions[target.value](
                self, args, kw, star_node, dstar_node
            )
        return Call(
            target, map(b,args), [(b(k),b(v)) for k,v in kw],
            star_node and b(star_node), dstar_node and b(dstar_node)
        )

    def parse(self, expr):
        return expressionSignature(ExprBuilder.parse(self, expr))


when(expressionSignature, codegen.And)
def do_intersect(expr):
    return reduce(intersect, map(expressionSignature, expr.values), True)

when(expressionSignature, codegen.Or)
def do_union(expr):
    return OrElse(map(expressionSignature, expr.values))


when(expressionSignature, codegen.Not)
def do_negate(expr):
    return negate(expressionSignature(expr.expr))

_mirror_ops = {
    '>': '<', '>=': '<=', '=>':'<=',
    '<': '>', '<=': '>=', '=<':'>=',
    '<>': '<>', '!=': '<>', '==':'==',
    'is': 'is', 'is not': 'is not'
}

when(expressionSignature, codegen.Compare)
def do_compare(expr):
    left = expr.expr
    (op, right), = expr.ops

    if isinstance(left, Const) and op in _mirror_ops:
        left, right, op = right, left, _mirror_ops[op]

    if isinstance(right, Const):
        if op=='in' or op=='not in':
            cond = compileIn(left, right.value)
            if cond is not None:
                return maybe_invert(cond, op=='in')
        elif op=='is' or op=='is not':
            return maybe_invert(compileIs(left, right.value), op=='is')
        else:
            return Test(Comparison(left), Inequality(op, right.value))

    # Both sides involve variables or an un-optimizable constant,
    #  so it's a generic boolean criterion  :(
    return Test(Truth(expr), Value(True))









def apply_meta(builder,
    (func, parsers, (argnames, varargs, varkw, defaults)), args, kw, star, dstar
):
    # NB: tuple-args not allowed!
    def parse(arg, node):
        if not node:
            return None
        return parsers.get(arg, build)(builder, node)

    data = {}
    extra = []
    offset = 0
    for name in argnames:
        if name=='__builder__': data[name] = builder
        elif name=='__star__':  data[name] = parse(name, star)
        elif name=='__dstar__': data[name] = parse(name, dstar)
        else:
            break
        offset += 1

    for k, v in zip(argnames[offset:], args):
        data[k] = parse(k, v)

    varargpos = len(argnames)-offset
    if len(args)> varargpos:
        if not varargs:
            raise TypeError("Too many arguments for %r" % (func,))
        extra.extend([parse(varargs, node) for node in args[varargpos:]])

    for k,v in kw:
        k = build(builder, k)
        assert type(k) is Const and isinstance(k.value, basestring)
        k = k.value
        if k in data:
            raise TypeError("Duplicate keyword %s for %r" % (k,func))

        if varkw and k not in argnames and k not in parsers:
            data[k] = parse(varkw,  v)
        else:
            data[k] = parse(k, v)

    if star and '__star__' not in data:
        raise TypeError("%r does not support parsing *args" % (func,))

    if dstar and '__dstar__' not in data:
        raise TypeError("%r does not support parsing **kw" % (func,))

    if defaults:
        for k,v in zip(argnames[-len(defaults):], defaults):
            data.setdefault(k, v)

    try:
        args = map(data.pop, argnames)+extra
    except KeyError, e:
        raise TypeError(
            "Missing positional argument %s for %r"%(e.args[0], func)
        )
    return func(*args, **data)


def compile_let(builder, args, kw, star, dstar):
    """Compile the let() function"""
    if args or star or dstar:
        raise TypeError("let() only accepts inline keyword arguments")

    for k,v in kw:
        k = build(builder, k)
        assert type(k) is Const and isinstance(k.value, basestring)
        k = k.value
        v = build(builder, v)
        builder.bind({k:v})
    return True

from peak.rules import let
meta_functions[let] = compile_let







def _expand_as(func, predicate_string, *namespaces):
    """Pre-parse predicate string and register meta function"""

    args, varargs, kw, defaults = arginfo = inspect.getargspec(func)
    argnames = list(flatten(filter(None, [args, varargs, kw])))
    parsed = parser.expr(predicate_string).totuple(1)[1]
    builder = CriteriaBuilder(
        dict([(arg,Local(arg)) for arg in argnames]), *namespaces
    )
    bindings = {}
    for b in builder.bindings[-len(namespaces):][::-1]:
        bindings.update(b)

    # Make a function that just gets the arguments we want
    c = Code.from_function(func)
    c.return_(Call(Const(locals),fold=False))
    getargs = new.function(
        c.code(), func.func_globals, func.func_name, func.func_defaults,
        func.func_closure
    )

    def expand(builder, *args):        
        builder.push(bindings)   # globals, locals, etc.
        builder.bind(apply_meta(builder, (getargs, {}, arginfo), *args))

        # build in the newly-isolated namespace
        result = build(builder, parsed) 
        builder.pop()
        return result

    meta_functions[func] = expand
    func.__doc__    # workaround for PyPy issue #1293
    c = Code.from_function(func)
    c.return_()
    if func.func_code.co_code == c.code().co_code:  # function body is empty
        c = Code.from_function(func)
        c.return_(build(builder, parsed))
        func.func_code = c.code()

    return func

def compileIs(expr, criterion):
    """Return a signature or predicate for 'expr is criterion'"""
    #if criterion is None:     # XXX this should be smarter
    #    return Test(IsInstance(expr), istype(NoneType))
    #else:
    return Test(Identity(expr), IsObject(criterion))

def maybe_invert(cond, truth):
    if not truth: return negate(cond)
    return cond

def compileIn(expr, criterion):
    """Return a signature or predicate (or None) for 'expr in criterion'"""
    try:
        iter(criterion)
    except TypeError:
        pass    # treat the in condition as a truth expression
    else:
        expr = Comparison(expr)
        return Test(expr, Disjunction([Value(v) for v in criterion]))

when(compileIn, (object, (type, ClassType)))
def compileInClass(expr, criterion):
    warn_parse("'x in SomeClass' syntax is deprecated; use 'isinstance(x,SomeClass)'")
    return Test(IsInstance(expr), Class(criterion))

when(compileIn, (object, istype))
def compileInIsType(expr, criterion):
    warn_parse("'x in istype(y)' syntax is deprecated; use 'type(x) is y'")
    return Test(IsInstance(expr), criterion)











def warn_parse(message, category=DeprecationWarning):
    """Issue a warning about a parsed string"""
    from warnings import warn, warn_explicit

    # Find the original call to _parse_string() to get its ParseContext
    import sys
    frame = sys._getframe(3)
    code = _parse_string.func_code
    ct = 2
    while frame is not None and frame.f_code is not code:
        frame = frame.f_back
        ct += 1
    if frame is None:
        # XXX direct use of expressionSignature; can't pinpoint a location
        return warn(message, category, ct)
    ctx = frame.f_locals['ctx']

    # Issue a warning against the method body
    g = ctx.globaldict
    #lineno = getattr(getattr(ctx.body, 'func_code', None), 'co_firstlineno', 2)
    module = g.get('__name__', "<string>")
    filename = g.get('__file__')
    if filename:
        fnl = filename.lower()
        if fnl.endswith(".pyc") or fnl.endswith(".pyo"):
            filename = filename[:-1]
    else:
        if module == "__main__":
            filename = sys.argv[0]
        if not filename:
            filename = module

    return warn_explicit(
        message, category, filename, ctx.lineno,
        g.setdefault("__warningregistry__", {})
    )





class IndexedEngine(Engine, TreeBuilder):
    """A dispatching engine that builds trees using bitmap indexes"""

    def __init__(self, disp):
        self.signatures = []
        self.all_exprs = {}
        super(IndexedEngine, self).__init__(disp)
        self.arguments = dict([(arg,Local(arg)) for arg in self.argnames])

    def _add_method(self, signature, rule):
        signature = Signature(tests_for(signature, self))
        if signature not in self.registry:
            case_id = len(self.signatures)
            self.signatures.append(signature)
            requires = []
            exprs = self.all_exprs
            for _t, expr, criterion in tests_for(signature, self):
                Ordering(self, expr).requires(requires)
                requires.append(expr)
                index_type = bitmap_index_type(self, expr)
                if index_type is not None:
                    if expr not in exprs:
                        exprs[expr] = 1
                        if always_testable(expr):
                            Ordering(self, expr).requires([])
                    index_type(self, expr).add_case(case_id, criterion)
        return super(IndexedEngine, self)._add_method(signature, rule)

    def _generate_code(self):
        smig = SMIGenerator(self.function)
        all_exprs = map(self.to_expression, self.all_exprs)
        for expr in all_exprs:
            smig.maybe_cache(expr)

        memo = dict([(expr, smig.action_id(expr)) for expr in all_exprs])
        return smig.generate(self.build_root(memo)).func_code

    def _full_reset(self):
        # Replace the entire engine with a new one
        Dispatching(self.function).create_engine(self.__class__)

    synchronized()
    def seed_bits(self, expr, cases):
        return BitmapIndex(self, expr).seed_bits(cases)

    synchronized()
    def reseed(self, expr, criterion):
        return BitmapIndex(self, expr).reseed(criterion)

    # Make build() a synchronized method
    build = synchronized(TreeBuilder.build.im_func)

    def build_root(self, memo):
        return self.build(
            to_bits([len(self.signatures)])-1, frozenset(self.all_exprs), memo
        )

    def best_expr(self, cases, exprs):
        return super(IndexedEngine, self).best_expr(
            list(from_bits(cases)), exprs
        )

    def build_node(self, expr, cases, remaining_exprs, memo):
        return memo[expr], predicate_node_for(
            self, expr, cases, remaining_exprs, memo
        )

    def selectivity(self, expr, cases):
        return BitmapIndex(self, expr).selectivity(cases)


    def to_expression(self, expr):
        return expr









    def build_leaf(self, cases, memo):
        action = self.rules.default_action
        signatures = self.signatures
        registry = self.registry
        for case_no in from_bits(cases):
            action = combine_actions(action, registry[signatures[case_no]])
        # No need to memoize here, since the combined action probably isn't
        # a meaningful key, and template-compiled methods are memoized at a
        # lower level anyway.
        return (0, compile_method(action, self))

when(bitmap_index_type,  (IndexedEngine, Truth))(lambda en,ex:TruthIndex)
when(predicate_node_for, (IndexedEngine, Truth))
def truth_node(builder, expr, cases, remaining_exprs, memo):
    dont_cares, seedmap = builder.seed_bits(expr, cases)
    return (    # True/false tuple for Truth
        builder.build(seedmap[True][0] | dont_cares, remaining_exprs, memo),
        builder.build(seedmap[False][0] | dont_cares, remaining_exprs, memo)
    )

when(bitmap_index_type,  (IndexedEngine, Identity))(lambda en,ex:PointerIndex)
when(predicate_node_for, (IndexedEngine, Identity))
def identity_node(builder, expr, cases, remaining_exprs, memo):
    dont_cares, seedmap = builder.seed_bits(expr, cases)
    return dict(
        [(seed, builder.build(inc|dont_cares, remaining_exprs, memo))
            for seed, (inc, exc) in seedmap.iteritems()]
    )

when(bitmap_index_type,  (IndexedEngine, Comparison))(lambda en,ex:RangeIndex)
when(predicate_node_for, (IndexedEngine, Comparison))
def range_node(builder, expr, cases, remaining_exprs, memo):
    dontcares, seedmap = builder.seed_bits(expr, cases)
    return split_ranges(
        dontcares, seedmap, lambda cases: builder.build(cases, remaining_exprs, memo)
    )

try: frozenset
except NameError: from core import frozenset


when(bitmap_index_type,  (IndexedEngine, type(None)))(value(None))

when(bitmap_index_type,  (IndexedEngine, (IsInstance, IsSubclass)))(
    value(TypeIndex)
)

when(predicate_node_for, (IndexedEngine, (IsInstance, IsSubclass)))
def class_node(builder, expr, cases, remaining_exprs, memo):
    dontcares, seedmap = builder.seed_bits(expr, cases)
    cache = {}
    def lookup_fn(cls):
        try:
            inc, exc = seedmap[cls]
        except KeyError:
            builder.reseed(expr, Class(cls))
            seedmap.update(builder.seed_bits(expr, cases)[1])
            inc, exc = seedmap[cls]
        cbits = dontcares | inc
        cbits ^= (exc & cbits)
        return cache.setdefault(cls, builder.build(cbits,remaining_exprs,memo))

    return cache, lookup_fn


abstract()
def type_to_test(typ, expr, engine):
    """Convert `typ` to a ``Test()`` of `expr` for `engine`"""

when(type_to_test, (type,))
when(type_to_test, (ClassType,))
def std_type_to_test(typ, expr, engine):
    return Test(IsInstance(expr), Class(typ))

when(type_to_test, (istype,))
def istype_to_test(typ, expr, engine):
    return Test(IsInstance(expr), typ)





when(tests_for, (istype(tuple), Engine))
def tests_for_tuple(ob, engine):
    for cls, arg in zip(ob, engine.argnames):
        yield type_to_test(cls, Local(arg), engine)

def always_testable(expr):
    """Is `expr` safe to evaluate in any order?"""
    return False

#when(always_testable, (IsSubclass,))   XXX might not be a class!

when(always_testable, ((Identity, Truth, Comparison, IsInstance),))
def testable_criterion(expr):
    return always_testable(expr.expr)

when(always_testable, ((Local, Const),))(value(True))


when(parse_rule, (IndexedEngine, basestring))
def _parse_string(engine, predicate, ctx, cls):
    b = CriteriaBuilder(engine.arguments, ctx.localdict, ctx.globaldict, __builtins__)
    expr = b.parse(predicate)
    bindings = b.bindings[0]
    if cls is not None and engine.argnames:
        cls = type_to_test(cls, engine.arguments[engine.argnames[0]], engine)
        expr = intersect(cls, expr)
    # XXX rewrap body for bindings here?  problem: CSE isn't ready
    # XXX so we'd have to make a temporary wrapper that gets replaced later. :(
    # XXX (the wrapper would just always recalc the values)
    # XXX Ugly bit at that point is that we're (slowly) generating code TWICE
    return Rule(
        maybe_bind(ctx.body, bindings), expr, ctx.actiontype, ctx.sequence
    )








def maybe_bind(func, bindings):
    """Apply expression bindings to arguments, if applicable"""

    if not bindings or not hasattr(func, 'func_code'):
        return func     # no bindings or not a function

    args, varargs, varkw, defaults = inspect.getargspec(func) 
    if not args or isinstance(args[0], basestring):
        return func # no args or first arg isn't a tuple

    for arg in args[0]:
        if not isinstance(arg, basestring):  # nested tuple arg, not a binding
            return func

    for arg in args[0]:
        if arg in bindings:
            for arg in args[0]:
                if arg not in bindings:
                    raise TypeError("Missing binding for %r" % arg)
            break
    else:
        return func     # none of the tuple args are in the binding

    argtuple = Tuple([bindings[arg] for arg in args[0]])

    c = Code.from_spec(func.func_name, args[1:], varargs, varkw)
    f = new.function(
        c.code(), func.func_globals, func.func_name, func.func_defaults
    )
    f.func_code = c.code()  # make f's signature match func w/out tuple
    c.return_(call_thru(f, Const(func), [argtuple]))    # call to match that
    f.func_code = c.code()  # now include the actual body
    f.__predicate_bindings__ = bindings, func   # mark for later optimization

    return f






# === As of this point, it should be possible to compile expressions!
#
meta_function(isinstance)(
    lambda __star__, __dstar__, *args, **kw:
        compileIsXCall(isinstance, IsInstance, args, kw, __star__, __dstar__)
)
meta_function(issubclass)(
    lambda __star__, __dstar__, *args, **kw:
        compileIsXCall(issubclass, IsSubclass, args, kw, __star__, __dstar__)
)
def compileIsXCall(func, test, args, kw, star, dstar):    
    if (
        kw or len(args)!=2 or not isinstance(args[1], Const)
        or isinstance(args[0], Const) or star is not None or dstar is not None
    ):
        return expressionSignature(
            Call(Const(func), args, tuple(kw.items()), star, dstar)
        )
    expr, seq = args
    return Test(test(expr), Disjunction(map(Class, _yield_tuples(seq.value))))

def _yield_tuples(ob):
    if type(ob) is tuple:
        for i1 in ob:
            for i2 in _yield_tuples(i1):
                yield i2
    else:
        yield ob

when(compileIs,
    # matches 'type(x) is y'
    "isinstance(expr,Call) and isinstance(expr.func, Const)"
    " and (expr.func.value is type) and len(expr.args)==1"
)
def compileTypeIsX(expr, criterion):
    return Test(IsInstance(expr.args[0]), istype(criterion))

when(expressionSignature, "isinstance(expr, Const) and isinstance(expr.value,priority)")
def test_for_priority(expr):
    return Test(None, expr.value)

