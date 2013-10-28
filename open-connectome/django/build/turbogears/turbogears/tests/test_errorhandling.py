import unittest
from turbogears.controllers import (error_handler, exception_handler,
    expose, validate, RootController, Controller)
from turbogears.errorhandling import FailsafeSchema
from turbogears.util import bind_args
from turbogears import validators
from turbogears import testutil


def _errors_to_str(errors):
    if isinstance(errors, dict):
        return dict(map(lambda (k, v): (k, str(v)), errors.iteritems()))
    else:
        return str(errors)

def setup_module():
    testutil.unmount()
    testutil.mount(MyRoot())
    testutil.mount(NestedController(), "/nestedcontroller")
    testutil.start_server()

def teardown_module():
    testutil.unmount()
    testutil.stop_server()

class MyRoot(RootController):

    def defaulterrorhandler(self, tg_source, tg_errors, tg_exceptions,
                            *args, **kw):
        return dict(title="Default error handler",
                    errors=_errors_to_str(tg_errors), args=args, kw=kw)

    def specialisederrorhandler(self, tg_source, tg_errors, *args, **kw):
        return dict(title="Specialised error handler",
                    errors=_errors_to_str(tg_errors), args=args, kw=kw)

    @expose()
    @validate(validators={'bar': validators.StringBoolean()})
    @error_handler(defaulterrorhandler)
    def defaulterror(self, bar=''):
        return dict(title="Default error provider")

    @expose()
    @validate(validators={'bar': validators.Int(not_empty=True),
        'baz': validators.Email()})
    @error_handler(specialisederrorhandler, "'baz' in tg_errors")
    @error_handler(defaulterrorhandler)
    def specialisederror(self, bar='', baz=''):
        return dict(title="Specialised error provider")

    @expose()
    @exception_handler(defaulterrorhandler)
    def exceptionerror(self):
        raise Exception("Exception 1")

    @expose()
    @exception_handler()
    def exceptionerror2(self):
        raise Exception("Exception 2")

    @expose()
    @validate(validators={'bar': validators.Int(not_empty=True)})
    @error_handler()
    def recursiveerror(self, tg_errors=None, bar=''):
        if tg_errors:
            return dict(title="Recursive error handler")
        else:
            return dict(title="Recursive error provider")

    @expose()
    @validate(validators={'bar': validators.Int(not_empty=True)})
    def impliciterror(self, tg_errors=None, bar=''):
        if tg_errors:
            return dict(title="Implicit error handler",
                        tg_errors=str(tg_errors))
        else:
            return dict(title="Implicit error provider")

    @expose()
    def normalmethod(self):
        return dict(title="Normal method")

    @expose()
    @validate(validators={'bar': validators.StringBoolean()})
    @error_handler(normalmethod)
    def normalmethodcaller(self, bar=''):
        return dict(title="Normal method caller")

    @expose()
    def infiniteloop(self):
        try:
            self.exceptionerror2()
        except Exception, e:
            return dict(title=str(e))
        else:
            return dict(title="Infinite loop provider")

    @expose()
    @validate(validators={'bar': validators.StringBoolean(),
        "second": validators.Int(not_empty=True)})
    @error_handler(defaulterrorhandler)
    def positionalargs(self, first, second, *args, **kw):
        return dict(title="Positional arguments", first=first, second=second,
                    third=args[0], args=args, bar=kw['bar'])

    @expose()
    @validate(validators={'bar': validators.Int(not_empty=True)})
    @error_handler(defaulterrorhandler)
    def missingargs(self, bar=''):
        return dict(title="Missing args provider")

    @expose()
    @validate(validators={'bar': validators.Int(not_empty=True)})
    def nohandler2(self, bar=''):
        return dict(title="No handler inner")

    @expose()
    def nohandler(self):
        try:
            self.nohandler2("abc")
        except NotImplementedError:
            return dict(title="Exception raised")
        else:
            return dict(title="No handler")

    def simpleerrorhandler(self, baz=None):
        return dict(title="Default error handler", baz=baz)

    @expose()
    @validate(validators={'bar':validators.Int(not_empty=True)})
    @error_handler(bind_args(baz=123)(simpleerrorhandler))
    def bindargs(self, bar=''):
        return dict(title="Bind arguments to error handler")

    @validate(validators={'bar': validators.Int(not_empty=True)})
    def notexposed(self, bar, tg_errors = None):
        if tg_errors:
            return dict(title="Not exposed error", bar=bar)
        else:
            return dict(title="Not exposed", bar=bar)

    @expose()
    def notexposedcaller(self, foo='', bar='', baz=''):
        return self.notexposed(bar)

    def continuation(self, tg_source):
        response = tg_source(self)
        response['continuation'] = True
        return response

    @expose()
    @validate(validators={'bar': validators.Int(not_empty=True)})
    @error_handler(continuation)
    def continuationcaller(self, bar=''):
        return dict(title="Continuation caller")

    @expose()
    @validate(validators={'bar': validators.Int(not_empty=True)})
    @error_handler(defaulterrorhandler)
    def nest(self, bar=''):
        return dict(title="Nested")

    @expose()
    @validate(validators={'bar': validators.Int(not_empty=True),
        'baz': validators.Int(not_empty=True)})
    def failsafenone(self, tg_errors=None, bar='', baz=''):
        return dict(title="No failsafe", bar=bar, baz=baz)

    @expose()
    @validate(validators={'bar': validators.Int(not_empty=True),
        'baz': validators.Int(not_empty=True)},
            failsafe_schema=FailsafeSchema.values,
            failsafe_values={'bar': 1, 'baz': 2})
    def failsafevaluesdict(self, tg_errors=None, bar='', baz=''):
        return dict(title="Failsafe values-dict", bar=bar, baz=baz)

    @expose()
    @validate(validators={'bar': validators.Int(not_empty=True),
        'baz': validators.Int(not_empty=True)},
              failsafe_schema=FailsafeSchema.values,
            failsafe_values=13)
    def failsafevaluesatom(self, tg_errors=None, bar='', baz=''):
        return dict(title="Failsafe values-atom", bar=bar, baz=baz)

    @expose()
    @validate(validators={'bar': validators.Int(not_empty=True),
        'baz': validators.Int(not_empty=True)},
              failsafe_schema=FailsafeSchema.map_errors)
    def failsafemaperrors(self, tg_errors=None, bar='', baz=''):
        return dict(title="Failsafe map errors", bar=str(bar), baz=str(baz))

    @expose()
    @validate(validators={'bar': validators.Int(
        if_invalid=1), 'baz': validators.Int(if_invalid=2)})
    def failsafeformencode(self, tg_errors=None, bar='', baz=''):
        return dict(title="Formencode if_invalid", bar=bar, baz=baz)

    @expose()
    @validate(validators={'bar': validators.Int(not_empty=True),
        'baz': validators.Int(not_empty=True)},
              failsafe_schema=FailsafeSchema.defaults)
    def failsafedefaults(self, tg_errors=None, bar=1, baz=2):
        return dict(title="Failsafe map defaults", bar=bar, baz=baz)


class NestedController(Controller):

    @expose()
    @validate(validators={'bar': validators.Int(not_empty=True)})
    @error_handler()
    def nest(self, bar=''):
        return dict(title="Nested")


app = testutil.make_app()

class TestErrorHandler(unittest.TestCase):

    def test_defaultErrorHandler(self):
        """Default error handler."""
        response = app.get('/defaulterror?bar=abc')
        self.assertTrue("Default error handler" in response)
        response = app.get('/defaulterror?bar=true')
        self.assertTrue("Default error provider" in response)

    def test_specialisedErrorHandler(self):
        """Error handler specialisation."""
        response = app.get('/specialisederror?bar=abc&baz=a@b.com')
        self.assertTrue("Default error handler" in response)
        response = app.get('/specialisederror?baz=abc&bar=1')
        self.assertTrue("Specialised error handler" in response)
        response = app.get('/specialisederror?bar=1&baz=a@b.com')
        self.assertTrue("Specialised error provider" in response)

    def test_exceptionErrorHandler(self):
        """Error handler for exceptions."""
        response = app.get('/exceptionerror')
        self.assertTrue("Default error handler" in response)

    def test_recursiveErrorHandler(self):
        """Recursive error handler."""
        response = app.get('/recursiveerror?bar=abc')
        self.assertTrue("Recursive error handler" in response)
        response = app.get('/recursiveerror?bar=1')
        self.assertTrue("Recursive error provider" in response)

    def test_implicitErrorHandler(self):
        """Implicit error handling."""
        response = app.get('/impliciterror?bar=abc')
        self.assertTrue("Implicit error handler" in response)
        response = app.get('/impliciterror?bar=1')
        self.assertTrue("Implicit error provider" in response)

    def test_normalMethodErrorHandler(self):
        """Normal method as an error handler."""
        response = app.get('/normalmethodcaller?bar=abc')
        self.assertTrue("Normal method" in response)
        response = app.get('/normalmethodcaller?bar=true')
        self.assertTrue("Normal method caller" in response)

    def test_infiniteRecursionPrevention(self):
        """Infinite recursion prevention."""
        response = app.get('/infiniteloop')
        self.assertTrue("Exception 2" in response)

    def test_positionalArgs(self):
        """Positional argument validation."""
        response = app.get('/positionalargs/first/23/third?bar=abc')
        self.assertTrue("Default error handler" in response)
        response = app.get('/positionalargs/first/abc/third?bar=false')
        self.assertTrue("Default error handler" in response)
        response = app.get('/positionalargs/first/abc/third?bar=abc')
        self.assertTrue("Default error handler" in response)
        response = app.get('/positionalargs/first/23/third?bar=true')
        self.assertTrue("Positional arguments" in response)
        self.assertTrue(response.raw['first'] == 'first')
        self.assertTrue(response.raw['second'] == 23)
        self.assertTrue(response.raw['third'] == 'third')

    def test_missingArgs(self):
        """Arguments required in validation missing."""
        response = app.get('/missingargs')
        self.assertTrue("Default error handler" in response)
        response = app.get('/missingargs?bar=12')
        self.assertTrue("Missing args provider" in response)

    def test_nohandler(self):
        """No error hanlder declared."""
        response = app.get('/nohandler')
        self.assertTrue("Exception raised" in response)

    def test_bindArgs(self):
        """Arguments can be bond to an error handler."""
        response = app.get('/bindargs')
        self.assertTrue("123" in response)

    def test_notExposed(self):
        """Validation error handling is decoupled from expose."""
        response = app.get('/notexposedcaller?foo=a&bar=rab&baz=c')
        self.assertTrue("Not exposed error" in response)
        self.assertTrue("rab" in response)

    def test_continuations(self):
        """Continuations via error handling mechanism."""
        response = app.get('/continuationcaller?bar=a')
        self.assertTrue("Continuation caller" in response)
        self.assertTrue(response.raw['continuation'] == True)

    def test_nested(self):
        """Potentially ambiguous cases."""
        response = app.get('/nest?bar=a')
        self.assertTrue("Default error handler" in response)
        response = app.get('/nestedcontroller/nest?bar=a')
        self.assertTrue("Nested" in response)

    def test_failsafe(self):
        """Failsafe values for erroneous input."""
        response = app.get('/failsafenone?bar=a&baz=b')
        self.assertTrue('"bar": "a"' in response)
        self.assertTrue('"baz": "b"' in response)
        response = app.get('/failsafevaluesdict?bar=a&baz=b')
        self.assertTrue('"bar": 1' in response)
        self.assertTrue('"baz": 2' in response)
        response = app.get('/failsafevaluesatom?bar=a&baz=b')
        self.assertTrue('"bar": 13' in response)
        self.assertTrue('"baz": 13' in response)
        response = app.get('/failsafemaperrors?bar=a&baz=b')
        self.assertTrue('"bar": "Please enter an integer value"' in response)
        self.assertTrue('"baz": "Please enter an integer value"' in response)
        response = app.get('/failsafeformencode?bar=a&baz=b')
        self.assertTrue('"bar": 1' in response)
        self.assertTrue('"baz": 2' in response)
        response = app.get('/failsafedefaults?bar=a&baz=b')
        self.assertTrue('"bar": 1' in response)
        self.assertTrue('"baz": 2' in response)
