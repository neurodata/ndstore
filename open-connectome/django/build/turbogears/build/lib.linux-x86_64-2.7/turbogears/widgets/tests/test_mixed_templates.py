
from turbogears import controllers, expose, testutil, widgets


def setup_module():
    global app
    app = testutil.make_app(MixedWidgetController)
    testutil.start_server()


def teardown_module():
    testutil.stop_server()



class SimpleValue(widgets.Widget):
    """Simple test widget with an unspecific template."""

    template = '<div id="${name}">${value}</div>'


class GenshiWrapper(widgets.Widget):
    """Simple wrapper widget using a Genshi template."""

    template = ('<div id="${name}" class="genshi"'
        ' xmlns:py="http://genshi.edgewall.org/" py:content="value()"/>')

    def default(self):
        return lambda: 'genshi'


class KidWrapper(widgets.Widget):
    """Simple wrapper widget using a Kid template."""

    template = ('<div id="${name}" class="kid"'
        ' xmlns:py="http://purl.org/kid/ns#" py:content="value()"/>')

    def default(self):
        return lambda: 'kid'


def test_external():
    """Test loading external templates with different engines."""
    w = widgets.Widget('foo', 'turbogears.widgets.tests.simple')
    assert w.engine_name == 'genshi'
    output = w.render('bar')
    assert output == '<div id="foo" class="genshi">bar</div>'
    w = widgets.Widget('bar', 'kid:turbogears.widgets.tests.simple')
    assert w.engine_name == 'kid'
    output = w.render('foo')
    assert output == '<div id="bar" class="kid">foo</div>'
    w = widgets.Widget('baz', 'turbogears.widgets.tests.simple',
        engine_name='kid')
    assert w.engine_name == 'kid'
    output = w.render('foe')
    assert output == '<div id="baz" class="kid">foe</div>'


def test_simple():
    """Test simple widget and specification of templating engine."""
    w = SimpleValue('foo')
    assert w.engine_name == 'genshi'
    output = w.render('bar')
    assert output == '<div id="foo">bar</div>'

    w = SimpleValue('bar', engine_name='kid')
    assert w.engine_name == 'kid'
    output = w.render('foo')
    assert output == '<div id="bar">foo</div>'

    class SimpleKidValue(SimpleValue):
        engine_name = 'kid'

    w = SimpleKidValue('foo')
    assert w.engine_name == 'kid'
    output = w.render('bar')
    assert output == '<div id="foo">bar</div>'


def test_wrapper():
    """Tests the wrapper widgets using both templating engines."""
    w = GenshiWrapper('foo')
    assert w.engine_name == 'genshi'
    output = w.render()
    assert output == '<div id="foo" class="genshi">genshi</div>'
    w = KidWrapper('bar')
    assert w.engine_name == 'kid'
    output = w.render()
    assert output == '<div id="bar" class="kid">kid</div>'


def test_nesting_same():
    """Test nesting widgets with the same templating engine."""
    foo = GenshiWrapper('foo')
    bar = GenshiWrapper('bar', default=lambda: foo)
    baz = GenshiWrapper('baz', default=lambda: bar)
    assert foo.engine_name == 'genshi'
    assert bar.engine_name == 'genshi'
    assert baz.engine_name == 'genshi'
    output = baz.render()
    assert (output == '<div id="baz" class="genshi">'
        '<div id="bar" class="genshi"><div id="foo" class="genshi">'
        'genshi</div></div></div>')
    foo = KidWrapper('foo')
    bar = KidWrapper('bar', default=lambda: foo)
    baz = KidWrapper('baz', default=lambda: bar)
    assert foo.engine_name == 'kid'
    assert bar.engine_name == 'kid'
    assert baz.engine_name == 'kid'
    output = baz.render()
    assert (output == '<div id="baz" class="kid">'
        '<div id="bar" class="kid"><div id="foo" class="kid">'
        'kid</div></div></div>')


def test_nesting_mixed():
    """Test nesting widgets with different templating engines."""
    foo = GenshiWrapper('foo')
    bar = KidWrapper('bar', default=lambda: foo)
    baz = GenshiWrapper('baz', default=lambda: bar)
    assert foo.engine_name == 'genshi'
    assert bar.engine_name == 'kid'
    assert baz.engine_name == 'genshi'
    output = baz.render()
    assert (output == '<div id="baz" class="genshi">'
        '<div id="bar" class="kid"><div id="foo" class="genshi">'
        'genshi</div></div></div>')
    foo = KidWrapper('foo')
    bar = GenshiWrapper('bar', default=lambda: foo)
    baz = KidWrapper('baz', default=lambda: bar)
    assert foo.engine_name == 'kid'
    assert bar.engine_name == 'genshi'
    assert baz.engine_name == 'kid'
    output = baz.render()
    assert (output == '<div id="baz" class="kid">'
        '<div id="bar" class="genshi"><div id="foo" class="kid">'
        'kid</div></div></div>')


class MixedWidgetController(controllers.RootController):

    @expose('genshi:turbogears.widgets.tests.widget')
    def genshi(self):
        """Show mixed widgets on a Genshi page template."""
        foo = GenshiWrapper('foo', default=lambda: widgets.Label('foo'))
        bar = KidWrapper('bar', default=lambda: foo)
        baz = GenshiWrapper('baz', default=lambda: bar)
        return dict(widget=baz)

    @expose('kid:turbogears.widgets.tests.widget')
    def kid(self):
        """Show mixed widgets on a Kid page template."""
        foo = KidWrapper('foo', default=lambda: widgets.Label('foo'))
        bar = GenshiWrapper('bar', default=lambda: foo)
        baz = KidWrapper('baz', default=lambda: bar)
        return dict(widget=baz)


def test_genshi_page():
    """Test displaying mixed widgets on a Genshi page template."""
    response = app.get('/genshi')
    output = response.body
    assert output.count('<html>') == 1 and output.count('</html>') == 1
    assert output.count('<body>') == 1 and output.count('</body>') == 1
    assert '<div id="baz" class="genshi">' in output
    assert '<div id="bar" class="kid">' in output
    assert '<div id="foo" class="genshi">' in output
    assert '<label id="foo" class="label">' in output
    assert '</label></div></div></div>' in output


def test_kid_page():
    """Test displaying mixed widgets on a Kid page template."""
    response = app.get('/kid')
    output = response.body
    assert output.count('<html>') == 1 and output.count('</html>') == 1
    assert output.count('<body>') == 1 and output.count('</body>') == 1
    assert '<div id="baz" class="kid">' in output
    assert '<div id="bar" class="genshi">' in output
    assert '<div id="foo" class="kid">' in output
    assert '<label id="foo" class="label">' in output
    assert '</label></div></div></div>' in output
