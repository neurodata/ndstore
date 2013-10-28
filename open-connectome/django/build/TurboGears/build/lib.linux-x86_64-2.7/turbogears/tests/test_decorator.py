import unittest

from turbogears.decorator import *


def d1(func):
    def call(func, *args, **kw):
        return func(*args, **kw)
    return call
d1 = decorator(d1)

def d2(func):
    def call(func, *args, **kw):
        return func(*args, **kw)
    return call
d2 = decorator(d2)

def d3(func):
    func.baz2 = 2
    def call(func, *args, **kw):
        return func(*args, **kw)
    return call
d3 = decorator(d3)

def foo(a, b):
    return a+b
foo.baz1 = 1

bar = foo

foo = d1(foo)
foo = d2(foo)
foo = d3(foo)

def addn(n):
    def entangle(func):
        def call(func, *args, **kw):
            return func(*args, **kw) + n
        return call
    return decorator(entangle)

@addn(11)
def py24(a):
    return a

@compose(addn(1), addn(2))
def composed(a):
    return a

def weakener():
    def entangle(func):
        def call(func, *args, **kw):
            return len(args)
        return call
    return weak_signature_decorator(entangle)

@weakener()
def weakling():
    pass

def sig_changer():
    def entangle(func):
        def call(func, a, b):
            return func(b)
        return call
    return decorator(entangle, (["a", "b"], None, None, None))

@sig_changer()
def new_sig(a):
    return a

@simple_decorator
def simple(func, *args, **kw):
    return func(*args, **kw) + 1

@simple_weak_signature_decorator
def simple_weakener(func, *args, **kw):
    return len(args)

@simple_weakener
def simple_weakling():
    pass

@simple
def simple_adder1(a):
    return a


class TestDecorator(unittest.TestCase):

    def test_preservation(self):
        for key, value in bar.__dict__.iteritems():
            self.assertTrue(key in foo.__dict__)
            self.assertTrue(value == foo.__dict__[key])
        self.assertTrue(bar.__name__ == foo.__name__)
        self.assertTrue(bar.__module__ == foo.__module__)
        self.assertTrue(bar.__doc__ == foo.__doc__)

    def test_eq(self):
        self.assertTrue(func_id(foo) == func_id(bar))
        self.assertTrue(func_eq(foo, bar))
        self.assertTrue(bar == func_original(foo))
        self.assertTrue(bar is func_original(foo))

    def test_history(self):
        self.assertTrue(len(func_composition(foo)) == 4)
        self.assertTrue(func_composition(foo)[:-1] ==
            func_composition(func_composition(foo)[-2]))

    def test_24compatibility(self):
        self.assertTrue(py24(2) == 13)

    def test_attributes(self):
        self.assertTrue(foo.baz1 == 1)
        self.assertTrue(foo.baz2 == 2)

    def test_composition(self):
        self.assertTrue(addn(3)(py24)(2) == 16)
        self.assertTrue(composed(1) ==  4, composed(1))
        self.assertTrue(composed.__name__ == "composed")

    def test_signature(self):
        self.assertTrue(make_weak_signature(bar)[1:3] == (
            "_decorator__varargs", "_decorator__kwargs"))
        self.assertTrue(weakling(1,2) == 2)
        self.assertTrue(new_sig(1,2) == 2)

    def test_simple_decorators(self):
        self.assertTrue(simple_adder1(1) == 2)
        self.assertTrue(simple_weakling(1, 2) == 2)
