from token import tok_name, NAME, NUMBER, STRING, ISNONTERMINAL, EQUAL
from symbol import sym_name
from new import instancemethod
import token, symbol, parser, sys

__all__ = [
    'parse_expr', 'build'
]

_name   = lambda builder,nodelist: builder.Name(nodelist[1])
_const  = lambda builder,nodelist: builder.Const(eval(nodelist[1]))


production = {
    NAME:   _name,
    NUMBER: _const,
    STRING: _const,
}


ops = {
    token.LEFTSHIFT: 'LeftShift',
    token.RIGHTSHIFT: 'RightShift',
    token.PLUS: 'Add',
    token.MINUS: 'Sub',
    token.STAR: 'Mul',
    token.SLASH: 'Div',
    token.PERCENT: 'Mod',
    token.DOUBLESLASH: 'FloorDiv',
}

def left_assoc(builder, nodelist):
    return getattr(builder,ops[nodelist[-2][0]])(nodelist[:-2],nodelist[-1])








def curry(f,*args):
    for arg in args:
        f = instancemethod(f,arg,type(arg))
    return f


def com_binary(opname, builder,nodelist):
    "Compile 'NODE (OP NODE)*' into (type, [ node1, ..., nodeN ])."
    items = [nodelist[i] for i in range(1,len(nodelist),2)]
    return getattr(builder,opname)(items)

# testlist: test (',' test)* [',']
# exprlist: expr (',' expr)* [',']
# subscriptlist: subscript (',' subscript)* [',']
testlist = testlist1 = exprlist = subscriptlist = curry(com_binary, 'Tuple')

# test: and_test ('or' and_test)* | lambdef
test = curry(com_binary, 'Or')

if sys.version>='2.5':
    or_test = test

    # test: or_test ['if' or_test 'else' test] | lambdef
    def test(builder, nodelist):
        return builder.IfElse(nodelist[1], nodelist[3], nodelist[5])

# and_test: not_test ('and' not_test)*
and_test = curry(com_binary, 'And')


# not_test: 'not' not_test | comparison
def not_test(builder, nodelist):
    return builder.Not(nodelist[2])








# comparison: expr (comp_op expr)*
def comparison(builder, nodelist):

    if len(nodelist)>4 and builder.simplify_comparisons:
        # Reduce (x < y < z ...) to (x<y and y<z and ...)
        return builder.And(
            [nodelist[:1]+nodelist[i:i+3] for i in range(1,len(nodelist)-1,2)]
        )

    results = []
    for i in range(3, len(nodelist), 2):
        nl = nodelist[i-1]

        # comp_op: '<' | '>' | '>=' | '<=' | '<>' | '!=' | '=='
        #          | 'in' | 'not' 'in' | 'is' | 'is' 'not'
        n = nl[1]
        if n[0] == token.NAME:
            type = n[1]
            if len(nl) == 3:
                if type == 'not':
                    type = 'not in'
                else:
                    type = 'is not'
        else:
            type = n[1]

        results.append((type, nodelist[i]))

    return builder.Compare(nodelist[1], results)


# expr: xor_expr ('|' xor_expr)*
expr = curry(com_binary, 'Bitor')

# xor_expr: and_expr ('^' and_expr)*
xor_expr = curry(com_binary, 'Bitxor')

# and_expr: shift_expr ('&' shift_expr)*
and_expr = curry(com_binary, 'Bitand')


# shift_expr: arith_expr ('<<'|'>>' arith_expr)*
# arith_expr: term (('+'|'-') term)*
# term: factor (('*'|'/'|'%'|'//') factor)*
shift_expr = arith_expr = term = left_assoc


unary_ops = {
    token.PLUS: 'UnaryPlus', token.MINUS: 'UnaryMinus', token.TILDE: 'Invert',
}


# factor: ('+'|'-'|'~') factor | power
def factor(builder, nodelist):
    return getattr(builder,unary_ops[nodelist[1][0]])(nodelist[2])



























# power: atom trailer* ['**' factor]

def power(builder, nodelist):
    if nodelist[-2][0]==token.DOUBLESTAR:
        return builder.Power(nodelist[:-2], nodelist[-1])

    node = nodelist[-1]
    nodelist = nodelist[:-1]
    t = node[1][0]

    # trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME

    if t == token.LPAR:
        return com_call_function(builder,nodelist,node[2])

    elif t == token.DOT:
        return builder.Getattr(nodelist, node[2][1])

    elif t == token.LSQB:
        item = node[2]

        while len(item)==2:
            item = item[1]

        if item[0]==token.COLON:
            lineno = item[2]
            return builder.Subscript(
                nodelist,
                (symbol.subscript, item, None)  # XXX optimization bypass
            )

        return builder.Subscript(nodelist, item)

    raise AssertionError("Unknown power", nodelist)







# atom: '(' [yield_expr|testlist_gexp] ')' |
#       '[' [listmaker] ']' |
#       '{' [dictmaker] '}' |
#       '`' testlist1 '`' |
#       NAME | NUMBER | STRING+

def atom(builder, nodelist):
    t = nodelist[1][0]
    if t == token.LPAR:
        if nodelist[2][0] == token.RPAR:
            return builder.Tuple(())
        return build(builder,nodelist[2])
    elif t==token.LSQB:
        if nodelist[2][0] == token.RSQB:
            return builder.List(())
        return listmaker(builder,nodelist[2])
    elif t==token.LBRACE:
        if nodelist[2][0] == token.RBRACE:
            items = ()
        else:
            dm = nodelist[2]
            items = [(dm[i],dm[i+2]) for i in range(1,len(dm),4)]
        return builder.Dict(items)
    elif t==token.BACKQUOTE:
        return builder.Backquote(nodelist[2])
    elif t==token.STRING:
        return builder.Const(eval(' '.join([n[1] for n in nodelist[1:]])))

    raise AssertionError("Unknown atom", nodelist)












# arglist: (argument ',')* (argument [',']| '*' test [',' '**' test] | '**' test)

def com_call_function(builder, primaryNode, nodelist):
    if nodelist[0] == token.RPAR:
        return builder.CallFunc(primaryNode,(),(),None,None)

    args = []; kw = []
    len_nodelist = len(nodelist)
    for i in range(1, len_nodelist, 2):
        node = nodelist[i]
        if node[0] == token.STAR or node[0] == token.DOUBLESTAR:
            break
        iskw, result = com_argument(node, kw)
        if iskw:
            kw.append(result)
        else:
            args.append(result)
    else:
        # No broken by star arg, so skip the last one we processed.
        i = i + 1

    if i < len_nodelist and nodelist[i][0] == token.COMMA:
        # need to accept an application that looks like "f(a, b,)"
        i = i + 1

    star_node = dstar_node = None
    while i < len_nodelist:
        tok = nodelist[i]
        ch = nodelist[i+1]
        i = i + 3
        if tok[0]==token.STAR:
            star_node = ch
        elif tok[0]==token.DOUBLESTAR:
            dstar_node = ch
        else:
            raise AssertionError, 'unknown node type: %s' % (tok,)

    return builder.CallFunc(primaryNode, args, kw, star_node, dstar_node)



# argument: [test '='] test [gen_for]  (Really [keyword '='] test)
# argument: test [gen_for] | test '=' test  # Really [keyword '='] test

def com_argument(nodelist, kw):
    if len(nodelist) == 2:
        if kw:
            raise SyntaxError, "non-keyword arg after keyword arg"
        return 0, nodelist[1]

    if nodelist[2][0] != token.EQUAL and len(nodelist)==3:
        return 0, (testlist_gexp.symbol, nodelist[1], nodelist[2])
    elif len(nodelist) !=4:
        raise AssertionError

    n = nodelist[1]
    while len(n) == 2 and n[0] != token.NAME:
        n = n[1]
    if n[0] != token.NAME:
        raise SyntaxError, "keyword can't be an expression (%r)" % (n,)

    return 1, ((token.STRING,`n[1]`,n[2]), nodelist[3])

# listmaker: test ( list_for | (',' test)* [','] )

def listmaker(builder, nodelist):

    values = []

    for i in range(1, len(nodelist)):

        if nodelist[i][0] == symbol.list_for:
            assert i==2 and len(nodelist)==3 and len(values)==1
            return com_iterator(builder.ListComp,values[0],nodelist[i])

        if nodelist[i][0] == token.COMMA:
            continue
        values.append(nodelist[i])

    return builder.List(values)


# list_iter: list_for | list_if
# list_for: 'for' exprlist 'in' testlist_safe [list_iter]
# list_if: 'if' old_test [list_iter]
#
# gen_iter: gen_for | gen_if
# gen_for: 'for' exprlist 'in' or_test [gen_iter]
# gen_if: 'if' old_test [gen_iter]

def com_iterator(method, value, nodelist):
    clauses = []
    nodelist = nodelist[1:]     # skip the symbol
    while nodelist:
        while len(nodelist)==1:
            nodelist, = nodelist
            nodelist = nodelist[1:]     # skip the symbol
        tok, val, line = nodelist[0]
        assert tok==NAME
        assert val in ('for', 'in', 'if')
        clauses.append((val, nodelist[1]))
        nodelist = nodelist[2:]
    return method(value, clauses)


# testlist_gexp test (gen_for | (',' test)* [','])

def testlist_gexp(builder, nodelist):
    if nodelist[2][0] == token.COMMA:
        return testlist(builder, nodelist)
    else:
        value, nodelist = nodelist[1:]
        return com_iterator(builder.GenExpr, value, nodelist)
    
testlist_comp = testlist_gexp   # Python 2.7

if hasattr(symbol, 'testlist_comp'):
    testlist_comp.symbol = symbol.testlist_comp
else:
    testlist_gexp.symbol = getattr(symbol, 'testlist_gexp', None)



# subscript: '.' '.' '.' | test | [test] ':' [test] [sliceop]
# sliceop: ':' [test]

def subscript(builder, nodelist):
    if nodelist[1][0]==token.DOT:
        return builder.Const(Ellipsis)

    item = nodelist; nl = len(nodelist)
    while type(item[1]) is tuple: item=item[1]   # find token, to get a line#
    lineno = item[-1]
    have_stride = nodelist[-1] and nodelist[-1][0]==symbol.sliceop
    if have_stride:
        start = stop = stride = None#; stride = (token.STRING, 'None', lineno)
        if len(nodelist[-1])==3:
            stride = nodelist[-1][2]
    else:
        start = None #(token.NUMBER,`0`,lineno)
        stop  = stride = None #(token.NUMBER,`sys.maxint`,lineno)

    if nl==5:
        start,stop = nodelist[1],nodelist[3]        # test : test sliceop
    elif nl==4:
        if nodelist[1][0]==token.COLON:             #   : test sliceop
            stop = nodelist[2]
        elif have_stride:                           # test :   sliceop
            start = nodelist[1]
        else:
            start, stop = nodelist[1], nodelist[3]  # test : test
    elif nl==3:
        if nodelist[1][0]==token.COLON:
            if not have_stride:
                stop = nodelist[2]      # : test
        else:
            start = nodelist[1]         # test :
    else:
        raise AssertionError("Unrecognized subscript", nodelist)
    if have_stride:
        return builder.Slice3(start,stop,stride)
    return builder.Slice2(start,stop)


for sym,name in sym_name.items():
    if name in globals():
        production[sym] = globals()[name]


def build(builder, nodelist):
    while len(nodelist)==2:
        nodelist = nodelist[1]
    return production[nodelist[0]](builder,nodelist)


def parse_expr(expr,builder):
    # include line numbers in parse data so valid symbols are never of length 2
    return build(builder, parser.expr(expr).totuple(1)[1])



























