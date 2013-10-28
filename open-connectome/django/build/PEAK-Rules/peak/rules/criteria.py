from peak.rules.core import *
from peak.rules.core import sorted, frozenset, set
from peak.util.decorators import struct
from weakref import ref
from sys import maxint
from peak.util.extremes import Min, Max
__all__ = [
    'Range', 'Value', 'IsObject', 'Class', 'tests_for',
    'Conjunction', 'Disjunction', 'Test', 'Signature',
    'Inequality', 'DisjunctionSet', 'OrElse', 'Intersection',
]

class Intersection(object):
    """Abstract base for conjunctions and signatures"""
    __slots__ = ()

class Disjunction(object):
    """Abstract base for DisjunctionSet and OrElse
    
    Note that a Disjunction can never have less than 2 members, as creating a
    Disjunction with only 1 item returns that item, and creating one with no
    items returns ``False`` (as no acceptable conditions means "never true").
    """
    __slots__ = ()

    def __new__(cls, input):
        if cls is Disjunction:
            return DisjunctionSet(input)
        return super(Disjunction, cls).__new__(cls)

when(negate, (Disjunction,))(lambda c: reduce(intersect, map(negate, c)))
        
struct()
def Range(lo=(Min,-1), hi=(Max,1)):
    if hi<=lo: return False
    return lo, hi

struct()
def Value(value, match=True):
    return value, match

when(implies, (Value, Range))(
    # ==Value implies Range if Value is within range
    lambda c1, c2: c1.match and c2.lo <= (c1.value, 0) <= (c2.hi)
)
when(implies, (Range, Value))(
    # Range implies !=Value if Value is out of range
    lambda c1, c2: not c2.match and not (c1.lo <= (c2.value, 0) <= (c1.hi)) or
                   c2.match and c1==Range((c2.value,-1), (c2.value,1))
)
when(implies, (Range, Range))(
    # Range1 implies Range2 if both points are within Range2's bounds
    lambda c1, c2: c1.lo >= c2.lo and c1.hi <= c2.hi
)
when(implies, (Value, Value))(
    lambda c1, c2: c1==c2 or (c1.match and not c2.match and c1.value!=c2.value)
)
when(intersect, (Range, Range))(
    lambda c1, c2: Range(max(c1.lo, c2.lo), min(c1.hi, c2.hi))
)

def to_range(v):
    lo, hi = (v.value, -1), (v.value, 1)
    if v.match:
        return Range(lo, hi)
    return Disjunction([Range(hi=lo), Range(lo=hi)])

when(intersect, (Value, Value))
def intersect_values(c1, c2):
    if c1==c2: return c1
    return intersect(to_range(c1), to_range(c2))

# if a value is a point inside a range, the implication rules would handle it;
# therefore, they are either !=values, or outside the range (and thus empty)
when(intersect, (Range, Value))(
    lambda c1, c2: not c2.match and intersect(c1, to_range(c2)) or False
)
when(intersect, (Value, Range))(
    lambda c1, c2: not c1.match and intersect(to_range(c1), c2) or False
)


when(negate, (Value,))(lambda c: Value(c.value, not c.match))
when(negate, (Range,))(lambda c: Disjunction([Range(hi=c.lo), Range(lo=c.hi)]))


struct()
def Class(cls, match=True):
    return cls, match

when(negate, (Class,))(lambda c: Class(c.cls, not c.match))

when(implies, (Class, Class))
def class_implies(c1, c2):
    if c1==c2:
        # not isinstance(x) implies not isinstance(x) always
        #     isinstance(x) implies isintance(x)      always
        return True
    elif c1.match and c2.match:
        #     isinstance(x) implies     isinstance(y) if issubclass(x,y)
        return implies(c1.cls, c2.cls)
    elif c1.match or c2.match:
        # not isinstance(x) implies     isinstance(x) never
        #     isinstance(x) implies not isinstance(y) never
        return False
    else:
        # not isinstance(x) implies not isinstance(y) if issubclass(y, x)
        return implies(c2.cls, c1.cls)

when(intersect, (Class, Class))(lambda c1,c2: Conjunction([c1, c2]))

when(implies, (istype, Class))(lambda c1,c2:
    c1.match and (c2.match == implies(c1.type, c2.cls)) # use ob/inst rules
)
when(implies, (Class, istype))(lambda c1,c2:
    c1.match and not c2.match and c1.cls is not c2.type
    and issubclass(c1.cls, c2.type)
)





struct()
def Test(expr, criterion):
    d = disjuncts(criterion)
    if len(d)!=1:
        return Disjunction([Test(expr, c) for c in d])
    return expr, criterion

when(negate, (Test,))(lambda c: Test(c.expr, negate(c.criterion)))

when(implies, (Test, Test))(
    lambda c1, c2: c1.expr==c2.expr and implies(c1.criterion, c2.criterion)
)

when(intersect, (Test, Test))
def intersect_tests(c1, c2):
    if c1.expr==c2.expr:
        return Test(c1.expr, intersect(c1.criterion, c2.criterion))
    else:
        return Signature([c1, c2])

inequalities = {
    '>':  lambda v: Range(lo=(v, 1)),
    '>=': lambda v: Range(lo=(v,-1)),
    '<':  lambda v: Range(hi=(v,-1)),
    '<=': lambda v: Range(hi=(v, 1)),
    '!=': lambda v: Value(v, False),
    '==': lambda v: Value(v, True),
}

inequalities['=<'] = inequalities['<=']
inequalities['=>'] = inequalities['>=']
inequalities['<>'] = inequalities['!=']

def Inequality(op, value):
    return inequalities[op](value)






class Signature(Intersection, tuple):
    """Represent and-ed Tests, in sequence"""

    __slots__ = ()

    def __new__(cls, input):
        output = []
        index = {}
        input = iter(input)
        for new in input:
            if new is True:
                continue
            elif new is False:
                return False
            assert isinstance(new, Test), \
                "Signatures can only contain ``criteria.Test`` instances"
            expr = new.expr
            if expr in index:
                posn = index[expr]
                old = output[posn]
                if old==new:
                    continue    # 'new' is irrelevant, skip it
                new = output[posn] = intersect(old, new)
                if new is False: return False
            else:
                index[expr] = len(output)
                output.append(new)

        if not output:
            return True
        elif len(output)==1:
            return output[0]
        return tuple.__new__(cls, output)

    def __repr__(self):
        return "Signature("+repr(list(self))+")"

when(negate, (Signature,))(lambda c: OrElse(map(negate, c)))



class IsObject(int):
    """Criterion for 'is' comparisons"""

    __slots__ = 'ref', 'match'

    def __new__(cls, ob, match=True):
        self = IsObject.__base__.__new__(cls, id(ob)&maxint)
        self.match = match
        self.ref = ob
        return self

    def __eq__(self,other):
        return self is other or (
            isinstance(other, IsObject) and self.match==other.match
            and self.ref is other.ref
        ) or (isinstance(other,(int,long)) and int(self)==other and self.match)

    def __ne__(self,other):
        return not (self==other)

    def __repr__(self):
        return "IsObject(%r, %r)" % (self.ref, self.match)

when(negate, (IsObject,))(lambda c: IsObject(c.ref, not c.match))

when(implies, (IsObject, IsObject))
def implies_objects(c1, c2):
    # c1 implies c2 if it's identical, or if c1=="is x" and c2=="is not y"
    return c1==c2 or (c1.match and not c2.match and c1.ref is not c2.ref)

when(intersect, (IsObject, IsObject))
def intersect_objects(c1, c2):
    #  'is x and is y'            'is not x and is x'
    if (c1.match and c2.match) or (c1.ref is c2.ref):
        return False
    else:
        # "is not x and is not y"
        return Conjunction([c1,c2])



class DisjunctionSet(Disjunction, frozenset):
    """Set of minimal or-ed conditions (i.e. no redundant/implying items)

    Note that a Disjunction can never have less than 2 members, as creating a
    Disjunction with only 1 item returns that item, and creating one with no
    items returns ``False`` (as no acceptable conditions means "never true").
    """
    def __new__(cls, input):
        output = []
        for item in input:
            for new in disjuncts(item):
                for old in output[:]:
                    if implies(new, old):
                        break
                    elif implies(old, new):
                        output.remove(old)
                else:
                    output.append(new)
        if not output:
            return False
        elif len(output)==1:
            return output[0]
        return frozenset.__new__(cls, output)

when(implies, (Disjunction, (object, Disjunction)))
def union_implies(c1, c2):  # Or(...) implies x if all its disjuncts imply x
    for c in c1:
        if not implies(c, c2):
            return False
    else:
        return True

when(implies, (object, Disjunction))
def ob_implies_union(c1, c2):   # x implies Or(...) if it implies any disjunct
    for c in c2:
        if implies(c1, c):
            return True
    else:
        return False


# We use @around for these conditions in order to avoid redundant implication
# testing during intersection, as well as to avoid ambiguity with the
# (object, bool) and  (bool, object) rules for intersect().
#
around(intersect, (Disjunction, object))(
    lambda c1, c2: type(c1)([intersect(x,c2) for x in c1])
)
around(intersect, (object, Disjunction))(
    lambda c1, c2: type(c2)([intersect(c1,x) for x in c2])
)
around(intersect, (Disjunction, Disjunction))(
    lambda c1, c2: type(c1)([intersect(x,y) for x in c1 for y in c2])
)
around(intersect, (Disjunction, Intersection))(
    lambda c1, c2: type(c1)([intersect(x,c2) for x in c1])
)
around(intersect, (Intersection, Disjunction))(
    lambda c1, c2: type(c2)([intersect(c1,x) for x in c2])
)

# XXX These rules prevent ambiguity with implies(object, bool) and
# (bool, object), at the expense of redundancy.  This can be cleaned up later
# when we allow cloning of actions for an existing rule.  (That is, when we can
# say "treat (bool, Disjunction) like (bool, object)" without duplicating the
# action.)
#
when(implies, (bool, Disjunction))(lambda c1, c2: not c1)
when(implies, (Disjunction, bool))(lambda c1, c2: c2)

# The disjuncts of a Disjunction are a list of its contents:
when(disjuncts, (DisjunctionSet,))(list)

abstract()
def tests_for(ob, engine=None):
    """Yield the tests composing ob, if any"""

when(tests_for, (Test,     ))(lambda ob, e: iter([ob]))
when(tests_for, (Signature,))(lambda ob, e: iter(ob))
when(tests_for, (bool,     ))(lambda ob, e: iter([]))


class Conjunction(Intersection, frozenset):
    """Set of minimal and-ed conditions (i.e. no redundant/implied items)

    Note that a Conjunction can never have less than 2 members, as
    creating a Conjunction with only 1 item returns that item, and
    creating one with no items returns ``True`` (since no required conditions
    means "always true").
    """
    def __new__(cls, input):
        output = []
        for new in input:
            for old in output[:]:
                if implies(old, new):
                    break
                elif implies(new, old):
                    output.remove(old)
                elif mutually_exclusive(new, old):
                    return False
            else:
                output.append(new)
        if not output:
            return True
        elif len(output)==1:
            return output[0]
        return frozenset.__new__(cls, output)

around(implies, (Intersection, object))
def set_implies(c1, c2):
    for c in c1:
        if implies(c, c2): return True
    else:
        return False

around(implies, ((Intersection, object), Intersection))
def ob_implies_set(c1, c2):
    for c in c2:
        if not implies(c1, c): return False
    else:
        return True


when(negate, (Conjunction,))(lambda c: Disjunction(map(negate, c)))

when(intersect, (istype,Class))
def intersect_type_class(c1, c2):
    if not c1.match: return Conjunction([c1,c2])
    return False

when(intersect, (Class, istype))
def intersect_type_class(c1, c2):
    if not c2.match: return Conjunction([c1,c2])
    return False

when(intersect, (istype,istype))
def intersect_type_type(c1, c2):
    # This is only called if there's no implication
    if c1.match or c2.match:
        return False    # so unless both are False matches, it's an empty set
    return Conjunction([c1, c2])

def mutually_exclusive(c1, c2):
    """Is the intersection of c1 and c2 known to be always false?"""
    return False

when(mutually_exclusive, (istype, istype))(
    lambda c1, c2: c1.match != c2.match and c1.type==c2.type
)















# Intersecting an intersection with something else should return a set of the
# same type as the leftmost intersection.  These methods are declared @around
# to avoid redundant implication testing during intersection, as well as to
# avoid ambiguity with the (object, bool) and  (bool, object) rules for
# intersect().
#
around(intersect, (Intersection, Intersection))(
    lambda c1, c2: type(c1)(list(c1)+list(c2))
)
around(intersect, (Intersection, object))(
    lambda c1, c2: type(c1)(list(c1)+[c2])
)
around(intersect, (object, Intersection))(
    lambda c1, c2: type(c2)([c1]+list(c2))
)

# Default intersection is a Conjunction
when(intersect, (object, object))(lambda c1, c2: Conjunction([c1,c2]))























class OrElse(Disjunction, tuple):
    """SEQUENCE of or-ed conditions (excluding redundant/implying items)"""

    def __new__(cls, input):
        output = []
        for item in input:
            for old in output[:]:
                if implies(item, old):
                    break
                elif implies(old, item):
                    output.remove(old)
            else:
                output.append(item)
        if not output:
            return False
        elif len(output)==1:
            return output[0]
        return tuple.__new__(cls, output)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, list(self))


when(disjuncts, (OrElse,))
def sequential_disjuncts(c):
    pre = True
    out = set()
    for cond in c:
        out.update(disjuncts(intersect(pre, cond)))
        pre = intersect(pre, negate(cond))
    return list(out)










