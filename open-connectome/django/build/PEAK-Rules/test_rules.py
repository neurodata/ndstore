import unittest, sys
from peak.rules.core import *

x2 = lambda a: a*2
x3 = lambda next_method, a: next_method(a)*3

class TypeEngineTests(unittest.TestCase):

    def testIntraSignatureCombinationAndRemoval(self):
        abstract()
        def f(a):
            """blah"""

        rx2 = Rule(x2,(int,), Method)
        rx3 = Rule(x3,(int,), Around)

        rules_for(f).add(rx2)
        self.assertEqual(f(1), 2)

        rules_for(f).add(rx3)
        self.assertEqual(f(1), 6)

        rules_for(f).remove(rx3)
        self.assertEqual(f(1), 2)

    def testAroundDecoratorAndRetroactiveCombining(self):
        def f(a):
            return a

        self.assertEqual(f(1), 1)
        self.assertEqual(f('x'), 'x')

        when(f, (int,))(x2)
        self.assertEqual(f(1), 2)
        self.assertEqual(f('x'), 'x')

        around(f, (int,))(lambda a:42)
        self.assertEqual(f(1), 42)
        self.assertEqual(f('x'), 'x')


class MiscTests(unittest.TestCase):

    def testPointers(self):
        from peak.rules.indexing import IsObject
        from sys import maxint
        anOb = object()
        ptr = IsObject(anOb)
        self.assertEqual(id(anOb)&maxint,ptr)
        self.assertEqual(hash(id(anOb)&maxint),hash(ptr))

        self.assertEqual(ptr.match, True)
        self.assertEqual(IsObject(anOb, False).match, False)
        self.assertNotEqual(IsObject(anOb, False), ptr)

        class X: pass
        anOb = X()
        ptr = IsObject(anOb)
        oid = id(anOb)&maxint
        self.assertEqual(oid,ptr)
        self.assertEqual(hash(oid),hash(ptr))
        del anOb
        self.assertNotEqual(ptr,"foo")
        self.assertEqual(ptr,ptr)
        self.assertEqual(hash(oid),hash(ptr))

    def testRuleSetReentrance(self):
        from peak.rules.core import Rule, RuleSet
        rs = RuleSet()
        log = []
        class MyListener:
            def actions_changed(self, added, removed):
                log.append(1)
                if self is ml1:
                    rs.unsubscribe(ml2)
        ml1, ml2 = MyListener(), MyListener()
        rs.subscribe(ml1)
        rs.subscribe(ml2)
        self.assertEqual(log, [])
        rs.add(Rule(lambda:None))
        self.assertEqual(log, [1, 1])

    def testAbstract(self):
        def f1(x,y=None):
            raise AssertionError("Should never get here")
        d = Dispatching(f1)
        log = []
        d.rules.default_action = lambda *args: log.append(args)
        f1 = abstract(f1)
        f1(27,42)
        self.assertEqual(log, [(27,42)])
        when(f1, ())(lambda *args: 99)
        self.assertRaises(AssertionError, abstract, f1)

    def testAbstractRegeneration(self):
        def f1(x,y=None):
            raise AssertionError("Should never get here")
        d = Dispatching(f1)
        log = []
        d.rules.default_action = lambda *args: log.append(args)
        d.request_regeneration()
        f1 = abstract(f1)
        self.assertNotEqual(d.backup, f1.func_code)
        self.assertEqual(f1.func_code, d._regen)
        f1.func_code = d.backup
        f1(27,42)
        self.assertEqual(log, [(27,42)])
        
    def testCreateEngine(self):
        def f1(x,y=None):
            raise AssertionError("Should never get here")
        d = Dispatching(f1)
        old_engine = d.engine
        self.assertEqual(d.rules.listeners, [old_engine])
        from peak.rules.core import TypeEngine
        class MyEngine(TypeEngine): pass
        d.create_engine(MyEngine)
        new_engine = d.engine
        self.assertNotEqual(new_engine, old_engine)
        self.failUnless(isinstance(new_engine, MyEngine))
        self.assertEqual(d.rules.listeners, [new_engine])


    def testIndexClassicMRO(self):
        class MyEngine: pass
        eng = MyEngine()
        from peak.rules.indexing import TypeIndex
        from peak.rules.criteria import Class
        from types import InstanceType
        ind = TypeIndex(eng, 'classes')
        ind.add_case(0, Class(MyEngine))
        ind.add_case(1, Class(object))
        ind.reseed(Class(InstanceType))
        self.assertEqual(
            dict(ind.expanded_sets()),
            {MyEngine: [[0,1],[]], InstanceType: [[1],[]], object: [[1],[]]}
        )

    def testEngineArgnames(self):
        argnames = lambda func: Dispatching(func).engine.argnames
        self.assertEqual(
            argnames(lambda a,b,c=None,*d,**e: None), list('abcde')
        )
        self.assertEqual(
            argnames(lambda a,b,c=None,*d: None), list('abcd')
        )
        self.assertEqual(
            argnames(lambda a,b,c=None,**e: None), list('abce')
        )
        self.assertEqual(
            argnames(lambda a,b,c=None: None), list('abc')
        )
        self.assertEqual(
            argnames(lambda a,(b,(c,d)), e: None), list('abcde')
        )

    def test_istype_implies(self):
        self.failUnless(implies(istype(object), object))
        self.failUnless(implies(istype(int), object))
        self.failIf(implies(istype(object, False), object))
        self.failIf(implies(istype(int, False), object))



    def testIndexedEngine(self):
        from peak.rules.predicates import IndexedEngine, Comparison
        from peak.rules.criteria import Range, Value, Test, Signature
        from peak.util.assembler import Local
        from peak.util.extremes import Min, Max
        abstract()
        def classify(age): pass
        Dispatching(classify).create_engine(IndexedEngine)
        def setup(r, f):
            when(classify, Signature([Test(Comparison(Local('age')), r)]))(f)
        setup(Range(hi=( 2,-1)), lambda age:"infant")
        setup(Range(hi=(13,-1)), lambda age:"preteen")
        setup(Range(hi=( 5,-1)), lambda age:"preschooler")
        setup(Range(hi=(20,-1)), lambda age:"teenager")
        setup(Range(lo=(20,-1)), lambda age:"adult")
        setup(Range(lo=(55,-1)), lambda age:"senior")
        setup(Value(16), lambda age:"sweet sixteen")

        self.assertEqual(classify(0),"infant")
        self.assertEqual(classify(25),"adult")
        self.assertEqual(classify(17),"teenager")
        self.assertEqual(classify(13),"teenager")
        self.assertEqual(classify(12.99),"preteen")
        self.assertEqual(classify(4),"preschooler")
        self.assertEqual(classify(55),"senior")
        self.assertEqual(classify(54.9),"adult")
        self.assertEqual(classify(14.5),"teenager")
        self.assertEqual(classify(16),"sweet sixteen")
        self.assertEqual(classify(16.5),"teenager")
        self.assertEqual(classify(99),"senior")
        self.assertEqual(classify(Min),"infant")
        self.assertEqual(classify(Max),"senior")

    def testSignatureOfTruthTests(self):
        from peak.rules.predicates import Truth        
        from peak.rules.criteria import Test, Signature
        # this line used to fail with a recursion error:
        Signature([Test(Truth(99), True), Test(Truth(88), False)])



    def testClassBodyRules(self):
        from peak.rules.core import Local, Rule
        from peak.rules.criteria import Signature, Test, Class, Value
        from peak.rules.predicates import IsInstance, Truth

        abstract()
        def f1(a): pass

        abstract()
        def f2(b): pass

        # This is to verify that the rules have sequence numbers by definition
        # order, not reverse definition order, inside a class.
        num = Rule(None).sequence
        
        class T:
            f1=sys._getframe(1).f_locals['f1']  # ugh
            when(f1)
            def f1_(a): pass

            f2=sys._getframe(1).f_locals['f2']
            when(f2, 'b')
            def f2_(b): pass

        self.assertEqual(
            list(rules_for(f1)), [Rule(T.f1_.im_func, (T,), Method, num+1)]
        )
        self.assertEqual(
            list(rules_for(f2)), [Rule(
                T.f2_.im_func, Signature([
                    Test(IsInstance(Local('b')), Class(T)),
                    Test(Truth(Local('b')), Value(True))
                ]), Method, num+2)
            ]
        )






    def testParseInequalities(self):
        from peak.rules.predicates import CriteriaBuilder, Comparison, Truth
        from peak.util.assembler import Compare, Local
        from peak.rules.criteria import Inequality, Test, Value
        from peak.rules.ast_builder import parse_expr
        builder = CriteriaBuilder(
            dict(x=Local('x'), y=Local('y')), locals(), globals(), __builtins__
        )
        pe = builder.parse

        x_cmp_y = lambda op, t=True: Test(
            Truth(Compare(Local('x'), ((op, Local('y')),))), Value(True, t)
        )      
        x,y = Comparison(Local('x')), Comparison(Local('y'))

        for op, mirror_op, not_op, stdop, not_stdop in [
            ('>', '<', '<=','>','<='),
            ('<', '>', '>=','<','>='),
            ('==','==','!=','==','!='),
            ('<>','<>','==','!=','=='),
        ]:
            fwd_sig = Test(x, Inequality(op, 1))
            self.assertEqual(pe('x %s 1' % op), fwd_sig)
            self.assertEqual(pe('1 %s x' % mirror_op), fwd_sig)

            rev_sig = Test(x, Inequality(mirror_op, 1))
            self.assertEqual(pe('x %s 1' % mirror_op), rev_sig)
            self.assertEqual(pe('1 %s x' % op), rev_sig)

            not_sig = Test(x, Inequality(not_op, 1))
            self.assertEqual(pe('not x %s 1' % op), not_sig)
            self.assertEqual(pe('not x %s 1' % not_op), fwd_sig)

            self.assertEqual(pe('x %s y' % op), x_cmp_y(stdop))
            self.assertEqual(pe('x %s y' % not_op), x_cmp_y(not_stdop))

            self.assertEqual(pe('not x %s y' % op),x_cmp_y(stdop,False))
            self.assertEqual(pe('not x %s y' % not_op),x_cmp_y(not_stdop,False))



    def testInheritance(self):
        class X: pass
        class Y(X): pass
        x = Y()
        f = lambda x: "f"
        when(f, "isinstance(x, X)")(lambda x: "g")
        when(f, "type(x) is X")(lambda x: "h")
        self.assertEqual(f(x), 'g')

    def testNotInherited(self):
        f = abstract(lambda x: "f")
        when(f, "not isinstance(x, int)")(lambda x: "g")
        when(f, "type(x) is object")(lambda x: "h")
        self.assertEqual(f(None), 'g')

    def testTypeImplicationAndIsSubclassOrdering(self):
        from inspect import isclass
        class A(object): pass
        class B(A): pass
        whats_this = abstract(lambda obj: obj)
        when(whats_this, "isclass(obj) and issubclass(obj, A)")(lambda o:"A")
        when(whats_this, "isclass(obj) and issubclass(obj, B)")(lambda o:"B")
        when(whats_this, (B,))(lambda o:"B()")
        when(whats_this, (A,))(lambda o:"A()")
        self.failUnlessEqual(whats_this(B), "B")
        self.failUnlessEqual(whats_this(A), "A")
        self.failUnlessEqual(whats_this(B()), "B()")
        self.failUnlessEqual(whats_this(A()), "A()")

    def testRuleSetClear(self):
        from peak.rules.core import Rule, RuleSet
        rs = RuleSet(); r = Rule(lambda:None,actiontype=Method)
        rs.add(r)
        self.assertEqual(list(rs), [r])
        rs.clear()
        self.assertEqual(list(rs), [])





    def testTypeEngineKeywords(self):
        def func(x, **k): pass
        def fstr(x,**k): return x,k
        abstract(func)
        when(func,(str,))(fstr)
        self.assertEqual(func('x',s='7'), ('x',{'s':'7'}))

    def testFlatPriorities(self):
        from peak.rules import value, AmbiguousMethods
        from peak.rules.predicates import priority
        
        f = lambda n, m: 0
        f1, f2, f3 = value(1), value(2), value(3)
        
        when(f, "n==5 and priority(1)")(f1)
        when(f, "m==5 and priority(1)")(f2)
        when(f, "n==5 and m==5 and priority(1)")(f3)
        self.assertEqual(f(5,5), 3)

    def testIsNot(self):
        def func(x): pass
        p,q,r = object(),object(),object()
        when(func,"x is not p")(value('~p'))
        when(func,"x is not p and x is not q and x is not r")(value('nada'))
        self.assertEqual(func(23),'nada')
        self.assertEqual(func(q),'~p')
        
    def testTypeVsIsTypePrecedence(self):
        def func(x): pass
        when(func, (int,        ))(value(1))
        when(func, (istype(int),))(value(2))
        self.assertEqual(func(42), 2)

    def testNamedGFExtension(self):
        p,q,r = object(),object(),object()
        when("%s:%s.named_func" % (__name__, self.__class__.__name__), "x is not p")(value('~p'))
        self.assertEqual(self.named_func(q),'~p')

    def named_func(x): pass
    named_func = staticmethod(named_func)

class RuleDispatchTests(unittest.TestCase):

    def testSimplePreds(self):
        from peak.rules import dispatch

        [dispatch.generic()]
        def classify(age):
            """Stereotype for age"""

        def defmethod(gf,s,func):
            gf.when(s)(func)

        defmethod(classify,'not not age<2', lambda age:"infant")
        defmethod(classify,'age<13', lambda age:"preteen")
        defmethod(classify,'age<5',  lambda age:"preschooler")
        defmethod(classify,'20>age', lambda age:"teenager")
        defmethod(classify,'not age<20',lambda age:"adult")
        defmethod(classify,'age>=55',lambda age:"senior")
        defmethod(classify,'age==16',lambda age:"sweet sixteen")
        self.assertEqual(classify(25),"adult")
        self.assertEqual(classify(17),"teenager")
        self.assertEqual(classify(13),"teenager")
        self.assertEqual(classify(12.99),"preteen")
        self.assertEqual(classify(0),"infant")
        self.assertEqual(classify(4),"preschooler")
        self.assertEqual(classify(55),"senior")
        self.assertEqual(classify(54.9),"adult")
        self.assertEqual(classify(14.5),"teenager")
        self.assertEqual(classify(16),"sweet sixteen")
        self.assertEqual(classify(16.5),"teenager")
        self.assertEqual(classify(99),"senior")
        self.assertEqual(classify(dispatch.strategy.Min),"infant")
        self.assertEqual(classify(dispatch.strategy.Max),"senior")








    def testKwArgHandling(self):
        from peak.rules import dispatch
        [dispatch.generic()]
        def f(**fiz): """Test of kw handling"""

        [f.when("'x' in fiz")]
        def f(**fiz): return "x"

        [f.when("'y' in fiz")]
        def f(**fiz): return "y"

        self.assertEqual(f(x=1),"x")
        self.assertEqual(f(y=1),"y")
        self.assertRaises(dispatch.AmbiguousMethod, f, x=1, y=1)

    def testVarArgHandling(self):
        from peak.rules import dispatch
        [dispatch.generic()]
        def f(*fiz): """Test of vararg handling"""

        [f.when("'x' in fiz")]
        def f(*fiz): return "x"

        [f.when("'y' in fiz")]
        def f(*fiz): return "y"

        self.assertEqual(f("foo","x"),"x")
        self.assertEqual(f("bar","q","y"),"y")
        self.assertEqual(f("bar","q","y"),"y")
        self.assertEqual(f("y","q",),"y")
        self.assertRaises(dispatch.AmbiguousMethod, f, "x","y")

    def test_NoApplicableMethods_is_raised(self):
        from peak.rules import dispatch
        [dispatch.generic()]
        def demo_func(number):
            pass
        demo_func.when("number < 10")(lambda x: 0)
        self.assertEqual(demo_func(3),0)
        self.assertRaises(dispatch.NoApplicableMethods, demo_func, 33)

    def testSingles(self):
        from peak.rules import dispatch        

        [dispatch.on('t')]
        def gm (t) : pass

        [gm.when(object)]
        def gm (t) : return 'default'

        [gm.when(int)]
        def gm2 (t) : return 'int'

        self.assertEqual(gm(42),"int")
        self.assertEqual(gm("x"),"default")
        self.assertEqual(gm(42.0),"default")


    def testSubclassDispatch(self):
        from peak.rules import dispatch        

        [dispatch.generic()]
        def gm (t) : pass

        [gm.when(dispatch.strategy.default)]
        def gm (t) : return 'default'

        [gm.when('issubclass(t,int)')]
        def gm2 (t) : return 'int'

        self.assertEqual(gm(int),"int")
        self.assertEqual(gm(object),"default")
        self.assertEqual(gm(float),"default")









    def testTrivialities(self):
        from peak.rules import dispatch        

        [dispatch.on('x')]
        def f1(x,*y,**z): "foo bar"

        [dispatch.on('x')]
        def f2(x,*y,**z): "baz spam"

        for f,doc in (f1,"foo bar"),(f2,"baz spam"):
            self.assertEqual(f.__doc__, doc)

            # Empty generic should raise NoApplicableMethods
            self.assertRaises(dispatch.NoApplicableMethods, f, 1, 2, 3)
            self.assertRaises(dispatch.NoApplicableMethods, f, "x", y="z")

            # Must have at least one argument to do dispatching
            self.assertRaises(TypeError, f)
            self.assertRaises(TypeError, f, foo="bar")






















class MockBuilder:
    def __init__(self, test, expr, cases, remaining, seeds, index=None):
        self.test = test
        self.args = expr, cases, remaining, {}
        self.seeds = seeds
        self.index = index

    def test_func(self, func):
        return func(self, *self.args)

    def build(self, cases, remaining_exprs, memo):
        self.test.failUnless(memo is self.args[-1])
        self.test.assertEqual(self.args[-2], remaining_exprs)
        return cases

    def seed_bits(self, expr, cases):
        self.test.assertEqual(self.args[1], cases)
        if self.index is not None:
            return self.index.seed_bits(cases)
        return self.seeds
        
    def reseed(self, expr, criterion):
        self.test.assertEqual(self.args[0], expr)
        self.index.reseed(criterion)

















class NodeBuildingTests(unittest.TestCase):

    def build(self, func, dontcare, seeds, index=None):
        seedbits = dontcare, seeds
        builder = MockBuilder(
            self, 'expr', 'cases', 'remaining', seedbits, index
        )
        return builder.test_func(func)

    def testTruthNode(self):
        from peak.rules.predicates import truth_node
        node = self.build(truth_node, 27,
            {True: (128,0), False: (64,0)})
        self.assertEqual(node, (27|128, 27|64))

    def testIdentityNode(self):
        from peak.rules.predicates import identity_node
        node = self.build(identity_node, 27,
            {9127: (128,0), 6499: (64,0), None: (0,0)})
        self.assertEqual(node, {None:27, 9127:27|128, 6499: 27|64})

    def testRangeNode(self):
        from peak.rules.indexing import RangeIndex, to_bits
        from peak.rules.predicates import range_node
        from peak.rules.criteria import Range, Value, Min, Max
        ind = RangeIndex(self, 'expr')
        ind.add_case(0, Value(19))
        ind.add_case(1, Value(23))
        ind.add_case(2, Value(23, False))
        ind.add_case(3, Range(lo=(57,1)))
        ind.add_case(4, Range(lo=(57,-1)))
        dontcare, seeds = ind.seed_bits(to_bits(range(6)))
        exact, ranges = self.build(range_node, dontcare, seeds)
        self.assertEqual(exact,
            {19:to_bits([0, 2, 5]), 23:to_bits([1,5]), 57:to_bits([2,4,5])})
        self.assertEqual(ranges,
            [((Min,57), to_bits([2,5])),  ((57,Max), to_bits([2,3,4,5]))])




    def testClassNode(self):
        from peak.rules.indexing import TypeIndex, to_bits
        from peak.rules.predicates import class_node
        from peak.rules.criteria import Class, Conjunction
        from types import InstanceType
        ind = TypeIndex(self, 'expr')
        class a: pass
        class b: pass
        class c(a,b): pass
        class x(a,b,object): pass

        ind.add_case(0, Class(InstanceType))
        ind.add_case(1, Conjunction([Class(a), Class(b), Class(c,False)]))
        ind.add_case(2, Class(object))
        ind.add_case(3, Conjunction([Class(a), Class(b)]))
        ind.add_case(4, Class(a))
        ind.selectivity(range(6))
        cases = to_bits(range(6))
        builder = MockBuilder(
            self, 'expr', cases, 'remaining', ind.seed_bits(cases), ind
        )
        cache, lookup = builder.test_func(class_node,)
        self.assertEqual(cache, {})
        data = [
            (object, to_bits([2,5])),
            (InstanceType, to_bits([0,2,5])),
            (a, to_bits([0,2,4,5])),
            (b, to_bits([0,2,5])),
            (c, to_bits([0,2,3,4,5])),
            (x, to_bits([1,2,3,4,5]))
        ]
        for k, v in data:
            self.assertEqual(lookup(k), v)
        self.assertEqual(cache, dict(data))
        
        





class DecompilationTests(unittest.TestCase):

    def setUp(self):
        from peak.rules.ast_builder import parse_expr
        from peak.rules.codegen import ExprBuilder        
        from peak.util.assembler import Local, Const
        from peak.rules.debug.decompile import decompile
        class Const(Const): pass    # non-folding
        class ExprBuilder(ExprBuilder):
            def Const(self,value): return Const(value)
        argmap = dict([(name,Local(name)) for name in 'abcdefgh'])
        builder = ExprBuilder(argmap, locals(), globals(), __builtins__)
        self.parse = builder.parse
        self.decompile = decompile

    def roundtrip(self, s1, s2=None):
        if s2 is None:
            s2 = s1
        self.check(self.parse(s1), s2)

    def check(self, expr, s):
        self.assertEqual(self.decompile(expr), s)

    def test_basics(self):
        from peak.util.assembler import Pass, Getattr, Local
        self.check(Pass, '')
        self.check(Getattr(Local('a'), 'b'), 'a.b')
        self.roundtrip('not -+~`a`')
        self.roundtrip('a+b-c*d/e%f**g//h')
        self.roundtrip('a and b or not c')
        self.roundtrip('~a|b^c&d<<e>>f')
        self.roundtrip('(a, b)')
        self.roundtrip('[a, b]')
        self.roundtrip('[a]')
        self.roundtrip('[]')
        self.roundtrip('()')
        self.roundtrip('1')
        self.roundtrip('a.b.c')
        # TODO: Compare


    def test_slices(self):
        self.roundtrip('a[:]')
        self.roundtrip('a[1:]')
        self.roundtrip('a[:2]')
        self.roundtrip('a[1:2]')
        self.roundtrip('a[1:2:3]')
        self.roundtrip('a[::]', 'a[:]')
        self.roundtrip('a[b:c:d]')
        self.roundtrip('a[b::d]')
        self.roundtrip('a[-b:c+d:e*f]')
        self.roundtrip('a[::d]')
        
    def test_paren_precedence(self):
        self.roundtrip('(1).__class__')
        self.roundtrip('1.2.__class__')
        self.roundtrip('`(a, b)`')
        self.roundtrip('`a,b`', '`(a, b)`')
        self.roundtrip('(a, [b, c])')
        self.roundtrip('a,b', '(a, b)')
        self.roundtrip('a+b*c')
        self.roundtrip('c*(a+b)')
        self.roundtrip('a*b*c')
        self.roundtrip('(a*b)*c', 'a*b*c')
        self.roundtrip('a*(b*c)')
        self.roundtrip('(a*b).c')
        self.roundtrip('(a, b, c)')
        self.roundtrip('a**b**c')
        self.roundtrip('a**(b**c)', 'a**b**c')
        self.roundtrip('a and b or c and not d')
        self.roundtrip('a and (b or c) and not d')

        if sys.version>='2.5':
            # if-else is right-associative
            self.roundtrip('(a, b, c) if d else e')
            self.roundtrip('(a if b else c) if d else e')
            self.roundtrip('a if (b if c else d) else e')
            self.roundtrip('a if b else (c if d else e)',
                           'a if b else c if d else e')



    def test_powers(self):
        # Exponentiation operator binds less tightly than unary numeric/bitwise
        # on the right:
        self.roundtrip('2**-1')
        self.roundtrip('2**+1')
        self.roundtrip('2**~1')
        self.roundtrip('2**1*2')
        self.roundtrip('2**(1*2)')
        
    def test_dicts(self):
        self.roundtrip('{}')
        self.roundtrip('{a: b}')
        self.roundtrip('{a: b, c: d}')

    def test_calls(self):
        self.roundtrip('1()')
        self.roundtrip('a()')
        self.roundtrip('a(b)')
        self.roundtrip('a(c=d)')
        self.roundtrip('a(*e)')
        self.roundtrip('a(**f)')
        self.roundtrip('a(b, c=d, *e, **f)')
        self.roundtrip('a.b(c)')
        self.roundtrip('a+b(c)')
        self.roundtrip('(a+b)(c)')
        if sys.version>='2.5':
            self.roundtrip('a if b(c) else d')
            self.roundtrip('a(b if c else d, *e if f else g)')





























def additional_tests():
    import doctest
    files = [
        'README.txt', 'DESIGN.txt', 'Indexing.txt', 'AST-Builder.txt',
        'Code-Generation.txt', 'Syntax-Matching.txt', 'Criteria.txt',
        'Predicates.txt', 
    ][sys.version<'2.4':]   # skip README.txt on 2.3 due to @ syntax
    return doctest.DocFileSuite(
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE,
        globs=dict(__name__=None),   # workaround PyPy type repr() issue 1292
         *files
    )





























