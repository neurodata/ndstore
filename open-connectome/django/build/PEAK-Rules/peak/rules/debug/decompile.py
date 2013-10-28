from peak.rules.core import when, value
from peak.util.assembler import *
from peak.rules.codegen import *

__all__ = ['precedence', 'associativity', 'decompile',]

def precedence(ob):
    """Get subexpression precedence - 0 is closest-binding precedence
    
    Subexpressions must be parenthesized when their parent expression has
    a lower return value from this function than they do.

    If the parent expression has equal precedence, then grouping is dependent
    upon associativity.
    """
    return 0

def associativity(ob):
    """Subexpression's operator associativity (0 for left, 1 for right)

    If a subexpression and parent expression have equal precedence, parentheses
    are needed unless the subexpression is in this position among the parent
    expression's operands.
    """
    return 0

when(associativity, (Power,) )(value(1))
when(associativity, (IfElse,))(value(2))
when(associativity, (ListOp,))(value(None))   

def needs_parens(parent, child, posn):
    """Does expression `child` need parens if it's at `posn` in `parent`?"""
    return False


def decompile(ob):
    return repr(ob)




prec_ops = (UnaryOp, BinaryOp, ListOp)

for prec, group in enumerate([
    (Tuple, List, Dict, Repr, ListComp, BuildSlice),
    (Getitem, GetSlice, Getattr, Call),
    (Power,), (Plus, Minus, Invert), (Mul, Div, FloorDiv, Mod), (Add, Sub),
    (LeftShift, RightShift), (Bitand,), (Bitxor,), (Bitor,),
    (Compare,), (Not,), (And,), (Or,), (IfElse,),    
]):
    when(precedence, (group,))(value(prec))
    for cls in group:
        if not issubclass(cls, prec_ops):
            prec_ops += (cls,)

when(needs_parens, (prec_ops, prec_ops))
def prec_parens(parent, child, posn):
    pprec = precedence(parent)
    pchild = precedence(child)
    if pprec < pchild: return True
    passoc = associativity(parent)
    return pprec==pchild and passoc is not None and posn != passoc 

when(needs_parens, (Power, (Plus, Minus, Invert)))
def prec_power(next_method, parent, child, posn):
    if posn==1: return False
    return next_method(parent, child, posn)

def decompiled_children(parent, children):
    for posn, child in enumerate(children):
        operand = decompile(child)
        if needs_parens(parent, child, posn):
            operand = '(%s)' % (operand,)
        yield operand
    

when(needs_parens, (Getattr, Const))
def int_parens(parent, child, pons):
    return decompile(child).isdigit()   # parenthesize integers



when(decompile, ((UnaryOp, BinaryOp, GetSlice, IfElse),))
def decompile_fmt(expr):
    return expr.fmt % tuple(decompiled_children(expr, expr[1:]))

when(decompile, (Local,))
def decompile_local(expr):
    return expr[1]

when(decompile, (Getattr,))
def decompile_getattr(expr):
    ignore, left, right = expr
    return '%s.%s' % (list(decompiled_children(expr, [left]))[0], right)

when(decompile, (Pass.__class__,))
def decompile_pass(expr):
    return ''

when(decompile, (Const,))
def decompile_const(expr):
    return decompile(expr.value)

when(decompile, (ListOp,))
def decompile_items(expr):
    return expr.fmt % ', '.join(decompiled_children(expr, expr[1]))

And.separator = ' and '
Or.separator = ' or '

when(decompile, ((And, Or),))
def decompile_sep(expr):
    return expr.separator.join(decompiled_children(expr, expr[1]))
    
when(decompile, (slice,))(
    lambda e: _decompile_slice(e.start, e.stop, e.step)
)
when(decompile, (BuildSlice,))(
    lambda e: _decompile_slice(e.start, e.stop, e.stride)
)



def _decompile_slice(start, stop, step):
    slice = ''
    if start is not None and start is not Pass: slice += decompile(start)
    slice +=':'
    if stop is not None and stop is not Pass: slice += decompile(stop)
    if step is not None and step is not Pass: slice += ':' + decompile(step)
    return slice

when(decompile, (Dict,))
def decompile_dict(expr):
    return '{%s}' % ', '.join(
        [('%s: %s' % tuple(map(decompile, args))) for args in expr[1]]
    )
    
when(decompile, (Call,))
def decompile_dict(expr):
    func = expr[1]
    if needs_parens(expr, func, 0):
        func = '(%s)' % (decompile(func),)
    else:
        func = decompile(func)
    return '%s(%s)' % (func, ', '.join(_decompiled_call_args(expr)))

def _decompiled_call_args(call):
    ignore, ignore, posargs, kwargs, star, dstar, ignore = call
    for arg in posargs:
        yield decompile(arg)
    for kw,arg in kwargs:
        yield '%s=%s' % (kw.value, decompile(arg))
    if star:
        yield '*' + decompile(star)
    if dstar:
        yield '**' + decompile(dstar)



    



















