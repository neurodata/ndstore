from peak.util.assembler import *
from codegen import *
from criteria import *
from predicates import *
from core import *
from token import NAME
from ast_builder import build

__all__ = ['match', 'Bind', 'match_predicate', 'match_sequence']

nodetype()
def Bind(name, code=None):
    if code is None:
        return name,
    raise TypeError("Can't compile Bind expression")

def match_predicate(pattern, expr, binds):
    """Return predicate matching pattern to expr, updating binds w/bindings"""
    return Test(Comparison(expr), Inequality('==', pattern))

when(match_predicate, (type(None),))
def match_none(pattern, expr, binds):
    return Test(Identity(expr), IsObject(pattern))

when(match_predicate, (Bind,))
def match_bind(pattern, expr, binds):
    if pattern.name != '_':
        vals = binds.setdefault(pattern.name, [])
        if expr not in vals:
            vals.append(expr)
            for old in vals[-2:-1]:
                return Test(Truth(Compare(expr, (('==', old),))), True)
    return True

class SyntaxBuilder(ExprBuilder):
    def Backquote(self, expr):
        while len(expr)==2: expr, expr = expr
        if expr[0]==NAME:
            return Bind(expr[1])
        raise SyntaxError("backquotes may only be used around an indentifier")

def match(expr, pattern):
    """Match `expr` against inline pattern `pattern`

    This function can only be called inside a rule string; the second argument
    is treated as a syntactic match pattern, which can include backquoted
    locals to be used as bind patterns."""
    raise NotImplementedError(
        "Use match_predicate() to match compiled patterns outside a rule"
    )

def build_pattern(builder, node):
    old = builder.__class__
    builder.__class__ = SyntaxBuilder
    try:
        return build(builder, node)
    finally:
        builder.__class__ = old

meta_function(match, pattern=build_pattern)
def compile_match(__builder__, expr, pattern):
    binds = {}
    pred = match_predicate(pattern, expr, binds)
    __builder__.bind(dict([(k, list(v)[0]) for k, v in binds.items()]))
    return pred

















when(match_predicate, (istype(list),))
when(match_predicate, (istype(tuple),))
def match_sequence(pattern, expr, binds):
   pred = Test(Comparison(Call(Const(len), (expr,))), Value(len(pattern)))
   for pos, item in enumerate(pattern):
       pred = intersect(
           pred, match_predicate(item, Getitem(expr, Const(pos)), binds)
       )
   return pred

when(match_predicate, (Node,))
def match_node(pattern, expr, binds):
   pred = Test(IsInstance(expr), istype(type(pattern)))
   for pos, item in enumerate(pattern):
       if pos:
           pred = intersect(
               pred, match_predicate(item, Getitem(expr, Const(pos)), binds)
           )
   return pred






















