from peak.util.assembler import *
from peak.util.symbols import Symbol
from peak.rules.core import gen_arg, clone_function
from ast_builder import build, parse_expr
from types import ModuleType
import sys
try:
    set
except NameError:
    from sets import Set as set

__all__ = [
    'GetSlice', 'BuildSlice', 'Dict', 'ExprBuilder', 'IfElse', 'CSECode',
    'UnaryOp', 'BinaryOp', 'ListOp',
]

nodetype(fmt='%s[%s:%s]')
def GetSlice(expr, start=Pass, stop=Pass, code=None):
    if code is None:
        if expr is not Pass:
            return fold_args(GetSlice, expr, start, stop)
        return expr, start, stop
    code(expr)
    if start is not Pass:
        code(start)
        if stop is not Pass:
            return code(stop, Code.SLICE_3)
        return code.SLICE_1()
    elif stop is not Pass:
        code(stop)
        return code.SLICE_2()
    return code.SLICE_0()


def module_to_ns(ns):
    if isinstance(ns, ModuleType):
        return ns.__dict__
    return ns



nodetype(fmt="%s:%s:%s")
def BuildSlice(start=Pass, stop=Pass, stride=Pass, code=None):
    if code is None:
        return fold_args(BuildSlice, start, stop, stride)
    if start is Pass: start = None
    if stop  is Pass: stop  = None
    code(start, stop, stride)
    if stride is not Pass:
        return code.BUILD_SLICE(3)
    return code.BUILD_SLICE(2)

nodetype()
def Dict(items, code=None):
    if code is None:
        return fold_args(Dict, tuple(map(tuple,items)))
    code.BUILD_MAP(0)
    for k,v in items:
        code.DUP_TOP()
        code(k, v)
        code.ROT_THREE()
        code.STORE_SUBSCR()

nodetype(fmt='%s if %s else %s')
def IfElse(tval, cond, fval, code=None):
    if code is None:
        return fold_args(IfElse, tval, cond, fval)
    else_clause, end_if = Label(), Label()
    code(cond)
    if tval != cond:
        code(else_clause.JUMP_IF_FALSE_OR_POP, tval)
        if code.stack_size is not None:
            code(end_if.JUMP_FORWARD)
    elif fval != cond:
        code(end_if.JUMP_IF_TRUE)

    if fval !=cond:       
        return code(else_clause, Code.POP_TOP, fval, end_if)
    else:
        return code(else_clause, end_if)


def unaryOp(name, (fmt, opcode)):
    if '%' not in fmt: fmt += '%s'
    nodetype(UnaryOp, fmt=fmt)
    def tmp(expr, code=None):
        if code is None:
            return fold_args(tmp, expr)
        return code(expr, opcode)
    tmp.__name__ = name
    return tmp

def binaryOp(name, (fmt, opcode)):
    if '%' not in fmt: fmt = '%s' + fmt + '%s'
    nodetype(BinaryOp, fmt=fmt)
    def tmp(left, right, code=None):
        if code is None:
            return fold_args(tmp, left, right)
        return code(left, right, opcode)
    tmp.__name__ = name
    return tmp

def listOp(name, (fmt, opcode)):
    nodetype(ListOp, fmt=fmt)
    def tmp(items, code=None):
        if code is None:
            return fold_args(tmp, tuple(items))
        code(*items)
        return opcode(code, len(items))
    tmp.__name__ = name
    return tmp

def mkOps(optype, **ops):
    return dict([(name,optype(name, op)) for (name, op) in ops.items()])

def globalOps(optype, **ops):
    __all__.extend(ops)
    localOps(globals(), optype, **ops)

def localOps(ns, optype, **ops):
    ns.update(mkOps(optype, **ops))


class UnaryOp(object):
    __slots__ = ()

class BinaryOp(object):
    __slots__ = ()

class ListOp(object):
    __slots__ = ()

globalOps(
    unaryOp,
    Not = ('not ', Code.UNARY_NOT),
    Plus = ('+', Code.UNARY_POSITIVE),
    Minus = ('-', Code.UNARY_NEGATIVE),
    Repr = ('`%s`', Code.UNARY_CONVERT),
    Invert = ('~', Code.UNARY_INVERT),
)

globalOps(
    binaryOp,
    Add = ('+', Code.BINARY_ADD),
    Sub = ('-', Code.BINARY_SUBTRACT),
    Mul = ('*', Code.BINARY_MULTIPLY),
    Div = ('/', Code.BINARY_DIVIDE),
    Mod = ('%s%%%s', Code.BINARY_MODULO),
    FloorDiv = ('//', Code.BINARY_FLOOR_DIVIDE),
    Power = ('**', Code.BINARY_POWER),
    LeftShift = ('<<', Code.BINARY_LSHIFT),
    RightShift = ('>>', Code.BINARY_RSHIFT),
    Getitem = ('%s[%s]', Code.BINARY_SUBSCR),
    Bitor = ('|', Code.BINARY_OR),
    Bitxor = ('^', Code.BINARY_XOR),
    Bitand = ('&', Code.BINARY_AND),
)

globalOps(
    listOp, Tuple = ('(%s)', Code.BUILD_TUPLE), List = ('[%s]', Code.BUILD_LIST)
)



class SMIGenerator:
    """State Machine Interpreter Generator"""
    
    ARG = Local('$Arg')
    SET_ARG = lambda self, code: code.STORE_FAST(self.ARG.name)
    WHY_CONTINUE = {'2.3':5}.get(sys.version[:3], 32)

    def __init__(self, func):
        import inspect
        self.code = code = CSECode.from_function(func) #, copy_lineno=True)
        self.actions = {}
        self.func = func
        self.first_action, loop_top, exit, bad_action = Label(), Label(), Label(), Label()
        args, star, dstar, defaults = inspect.getargspec(func)
        actions, self.actions_const = self.make_const({})
        start_node, self.startnode_const = self.make_const(object())

        code.cache(None)    # force CSE preamble here
        code(start_node, loop_top)
        code.UNPACK_SEQUENCE(2)     # action, argument
        code(
            exit.JUMP_IF_FALSE,
            Compare(Code.DUP_TOP, (('in', actions),)),
            bad_action.JUMP_IF_FALSE_OR_POP,
            Code.ROT_TWO,   # argument, action
            self.SET_ARG,   # action
            self.dispatch_handler,
        exit,
            Code.POP_TOP,       # drop action, leaving argument
            Return(
                Call(Pass, map(gen_arg, args),(),gen_arg(star), gen_arg(dstar))
            ),
        bad_action,
            Code.POP_TOP,
            Return(Call(Const(self.bad_action),(Code.ROT_THREE, Code.ROT_TWO))),
        self.first_action,
        )
        self.NEXT_STATE = loop_top.JUMP_ABSOLUTE
        self.maybe_cache = code.maybe_cache


    def generate(self, start_node):
        func = clone_function(self.func)
        self.code.co_consts[self.startnode_const] = start_node
        self.code.co_consts[self.actions_const] = dict.fromkeys(
            self.actions.values()
        )
        func.func_code = self.code.code()
        return func

    def make_const(self, value):
        self.code.co_consts.append(value)
        return Const(value), len(self.code.co_consts)-1

    def action_id(self, expression):
        try:
            return self.actions[expression]
        except KeyError:
            action = self.actions[expression] = self.code.here()
            self.code_action(action, expression)
            return action

    def bad_action(self, action, argument):
        raise AssertionError("Invalid action: %s, %s" % (action, argument))

    def next_state(self, code):
        if code.stack_size is not None:
            code(self.NEXT_STATE)

    def dispatch_handler(self, code):
        fake = Label()
        code(
            fake.SETUP_LOOP, self.WHY_CONTINUE, Code.END_FINALLY,
            Code.POP_BLOCK, fake, Return(Pass),  # <- all dead code, never runs
        )

    def code_action(self, action, expression):
        self.code.stack_size = 0
        self.code(expression, self.next_state)



    if '__pypy__' in sys.builtin_module_names:

        # Use a linear search in place of computed goto - PyPy handles
        # finally: blocks in a way that prevents computed goto from working

        def dispatch_handler(self, code):
            code(self.first_action.JUMP_FORWARD)
    
        def code_action(self, action, expression):
            self.code.stack_size = 1
            next_action = Label()
            self.code(
                Compare(Code.DUP_TOP, (('==', action),)),
                next_action.JUMP_IF_FALSE_OR_POP,
                Code.POP_TOP, expression,
                self.next_state,next_action, Code.POP_TOP
            )
























CACHE = Local('$CSECache')
SET_CACHE = lambda code: code.STORE_FAST(CACHE.name)

class CSETracker(Code):
    """Helper object that tracks common sub-expressions"""

    def __init__(self):
        super(CSETracker, self).__init__()
        self.cse_depends = {}

    def track(self, expr):
        self.track_stack = [None, 0]
        self.to_cache = []
        try:
            self(expr)
            return self.to_cache
        finally:
            del self.track_stack, self.to_cache

    def __call__(self, *args):
        scall = super(CSETracker, self).__call__
        ts = self.track_stack
        for ob in args:           
            ts[-1] += 1
            ts.append(ob)
            ts.append(0)
            try:
                before = self.stack_size
                scall(ob)
            finally:
                count = ts.pop()
                ts.pop()
            if count and callable(ob) and self.stack_size==before+1:
                # Only consider non-leaf callables for caching
                top = tuple(ts[-2:])
                if self.cse_depends.setdefault(ob, top) != top:
                    if ob not in self.to_cache:
                        self.to_cache.append(ob)



class CSECode(Code):
    """Code object with common sub-expression caching support"""

    def __init__(self):
        super(CSECode, self).__init__()
        self.expr_cache = {}
        self.tracker = CSETracker()
        
    def cache(self, expr):
        if not self.expr_cache:
            self.LOAD_CONST(None)
            self.STORE_FAST(CACHE.name)
        self.expr_cache.setdefault(
            expr, "%s #%d" % (expr, len(self.expr_cache)+1)
        )

    def maybe_cache(self, expr):
        map(self.cache, self.tracker.track(expr))

    def __call__(self, *args):
        scall = super(CSECode, self).__call__
        for ob in args:
            if callable(ob) and ob in self.expr_cache:
                key = self.expr_cache[ob]
                def calculate(code):
                    scall(ob, Code.DUP_TOP, CACHE, Const(key), Code.STORE_SUBSCR)
                cache = IfElse(
                    CACHE, CACHE, lambda c: scall({}, Code.DUP_TOP, SET_CACHE)
                )
                scall(
                    IfElse(
                        Getitem(CACHE, Const(key)),
                        Compare(Const(key), [('in', cache)]),
                        calculate
                    )
                )
            else:
                scall(ob)



class ExprBuilder:
    """Expression builder returning bytecode-able AST nodes"""

    def __init__(self,arguments,*namespaces):
        self.bindings = [
            dict([(k,self.Const(v)) for k,v in module_to_ns(ns).iteritems()]) for ns in namespaces
        ]
        self.push(arguments); self.push()

    def push(self, ns={}): self.bindings.insert(0, {}); self.bind(ns)
    def bind(self, ns): self.bindings[0].update(ns)
    def pop(self): return self.bindings.pop(0)        
    def parse(self, expr): return parse_expr(expr, self)
    def Const(self,value): return Const(value)

    def Name(self,name):
        for ns in self.bindings:
            if name in ns: return ns[name]
        raise NameError(name)

    def Subscript(self, left, right):
        expr = build(self,left)
        key =  build(self,right)
        if isinstance(key, GetSlice):
            return GetSlice(expr, key.start, key.stop)
        return Getitem(expr, key)

    def Slice2(self, start, stop):
        start = start and build(self, start) or Pass
        stop  = stop  and build(self, stop ) or Pass
        return GetSlice(Pass, start, stop)

    def Slice3(self, start, stop, stride):
        start  = start  and build(self, start ) or Pass
        stop   = stop   and build(self, stop  ) or Pass
        stride = stride and build(self, stride) or Pass
        return BuildSlice(start, stop, stride)

    def Getattr(self, expr, attr):
        return Getattr(build(self,expr), attr)

    simplify_comparisons = False

    def Compare(self, expr, ops):
        return Compare(
            build(self, expr),
            [(op=='<>' and '!=' or op, build(self,arg)) for op, arg in ops]
        )

    def _unaryOp(name, nt):
        def method(self, expr):
            return nt(build(self,expr))
        return method

    localOps(locals(), _unaryOp,
        UnaryPlus  = Plus,
        UnaryMinus = Minus,
        Invert     = Invert,
        Backquote  = Repr,
        Not        = Not,
    )

    del _unaryOp

    def _mkBinOp(name, nt):
        def method(self, left, right):
            return nt(build(self,left), build(self,right))
        return method

    localOps(locals(), _mkBinOp,
        Add        = Add,
        Sub        = Sub,
        Mul        = Mul,
        Div        = Div,
        Mod        = Mod,
        FloorDiv   = FloorDiv,
        Power      = Power,
        LeftShift  = LeftShift,
        RightShift = RightShift,
    )
    del _mkBinOp

    def _multiOp(name, nt):
        def method(self, items):
            result = build(self,items[0])
            for item in items[1:]:
                result = nt(result, build(self,item))
            return result
        return method

    localOps(locals(), _multiOp,
        Bitor  = Bitor,
        Bitxor = Bitxor,
        Bitand = Bitand,
    )
    del _multiOp

    def _listOp(name, op):
        def method(self,items):
            return op(map(build.__get__(self), items))
        return method

    localOps(locals(), _listOp,
        And   = And,
        Or    = Or,
        Tuple = Tuple,
        List  = List,
    )

    def Dict(self, items):
        b = build.__get__(self)
        return Dict([(b(k),b(v)) for k,v in items])

    def CallFunc(self, func, args, kw, star_node, dstar_node):
        b = build.__get__(self)
        return Call(
            b(func), map(b,args), [(b(k),b(v)) for k,v in kw],
            star_node and b(star_node), dstar_node and b(dstar_node)
        )

    def IfElse(self, tval, cond, fval):
        return IfElse(build(self,tval), build(self,cond), build(self,fval))

