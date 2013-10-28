try:
    from json import dumps, loads
except ImportError: # Python < 2.6
    from simplejson import dumps, loads

from turbogears import controllers, expose, view
from turbogears.testutil import make_app, start_server, stop_server


def setup_module():
    start_server()
    options = dict(strict=True, cache=True)
    view.engines['testplugin'] = TestTemplateEngine(options=options)

def teardown_module():
    stop_server()


class TestTemplateEngine(object):
    """A minimal Buffet template engine plugin for testing."""

    def __init__(self, extra_vars_func=None, options=None):
        self.extra_vars_func = extra_vars_func
        self.options = options or dict()

    def render(self, info, format=None, fragment=False, template=None,
               **options):
        try:
            info.update(self.extra_vars_func())
        except TypeError:
            pass

        opts = self.options.copy()
        opts.update(options)

        return dumps((info, opts))

    def load_template(self, templatename):
        pass

    def transform(self, info, template):
        pass


class ExposeRoot(controllers.RootController):

    @expose('kid:turbogears.tests.simple')
    @expose('json')
    def with_json(self):
        return dict(title='Foobar', mybool=False, someval='foo')

    @expose('kid:turbogears.tests.simple')
    @expose('json', accept_format='application/json', as_format='json')
    @expose('cheetah:turbogears.tests.textfmt', accept_format='text/plain')
    def with_json_via_accept(self):
        return dict(title='Foobar', mybool=False, someval='foo')

    @expose('testplugin:test', strict=False, renderer='fast')
    def with_testplugin(self):
        return dict(fruit='apple', tree='Rowan')

    @expose('testplugin:test', mapping=dict(deprecated=True))
    def with_testplugin_using_mapping(self):
        return dict(fruit='apple', tree='Rowan')

def test_gettinghtml():
    app = make_app(ExposeRoot)
    response = app.get('/with_json')
    assert "Paging all foo" in response

def test_gettingjson():
    app = make_app(ExposeRoot)
    response = app.get('/with_json?tg_format=json')
    assert '"title": "Foobar"' in response

def test_gettingjsonviaaccept():
    app = make_app(ExposeRoot)
    response = app.get('/with_json_via_accept',
            headers=dict(Accept='application/json'))
    assert '"title": "Foobar"' in response

def test_getting_json_with_accept_but_using_tg_format():
    app = make_app(ExposeRoot)
    response = app.get('/with_json_via_accept?tg_format=json')
    assert '"title": "Foobar"' in response

def test_getting_plaintext():
    app = make_app(ExposeRoot)
    response = app.get('/with_json_via_accept',
        headers=dict(Accept='text/plain'))
    assert response.body == "This is a plain text for foo."

def test_allow_json():

    class NewRoot(controllers.RootController):
        @expose('turbogears.tests.doesnotexist', allow_json=True)
        def test(self):
            return dict(title='Foobar', mybool=False, someval='niggles')

    app = make_app(NewRoot)
    response = app.get('/test', headers= dict(accept='application/json'))
    values = loads(response.body)
    assert values == dict(title='Foobar', mybool=False, someval='niggles',
        tg_flash=None)
    assert response.headers['Content-Type'] == 'application/json'
    response = app.get('/test?tg_format=json')
    values = loads(response.body)
    assert values == dict(title='Foobar', mybool=False, someval='niggles',
        tg_flash=None)
    assert response.headers['Content-Type'] == 'application/json'

def test_expose_pass_options():
    """Test that expose correctly passes kwargs as options to template engine."""
    app = make_app(ExposeRoot)
    response = app.get('/with_testplugin')
    info, options = loads(response.body)
    assert info['fruit'] == 'apple' and info['tree'] == 'Rowan', \
        "Data dict returned from exposed method not included in output."
    assert options['cache'] is True, \
        "Options passed to template engine constructor not used."
    assert options['renderer'] == 'fast', \
        "Options passed as kwargs to expose() not passed to render()."
    assert options['strict'] is not True, \
        "Options passed to expose() do not override options passed to __init__()."
    response = app.get('/with_testplugin_using_mapping')
    info, options = loads(response.body)
    assert options['mapping'] == dict(deprecated=True), \
        "Options passed in mapping arg to expose() not passed to render()."

