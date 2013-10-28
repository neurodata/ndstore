
import os

from turbogears import (config, controllers, expose, testutil,
    validators, view, widgets)
from turbogears.testutil import catch_validation_errors


def setup_module():
    testutil.start_server()


def teardown_module():
    testutil.stop_server()


def check_trace_bug():
    """Check for Python issue 1569356.

    This appears when run with coverage on Python < 2.6.

    """
    class A:
        pass
    class B:
        def b(self):
            return A()
    return 'A' in B.__dict__

has_trace_bug = check_trace_bug()


def test_rendering_without_engine():
    """Helpful error when rendering widgets with no templating engine loaded"""
    engines = view.engines
    view.engines = {}
    try:
        widgets.CSSLink('foo')()
    except Exception, msg:
        msg = str(msg)
    else:
        msg = 'No error'
    view.engines = engines
    assert 'templating engine is not installed or not yet loaded' in msg


def test_label():
    """Tests simple labels"""
    label = widgets.Label('foo')
    rendered = label.render("The Foo", format='xhtml')
    assert """<label id="foo" class="label">The Foo</label>""" == rendered


def test_default_value():
    """Widgets can have a default value"""
    textfield = widgets.TextField('name')
    output = textfield.render(format='xhtml')
    assert 'value' not in output
    textfield = widgets.TextField('name', default='ed kowalczyk')
    output = textfield.render(format='xhtml')
    assert 'value="ed kowalczyk"' in output


def test_callable_default_value():
    """Widgets can have a callable default value"""
    textfield = widgets.TextField('name', default=lambda: 'chad taylor')
    output = textfield.render(format='xhtml')
    assert 'value="chad taylor"' in output


def test_false_default_value():
    """Widgets can have a default value that evaluates to False"""
    textfield = widgets.TextField('name')
    assert textfield.default is None
    output = textfield.render(format='xhtml')
    assert 'value' not in output
    textfield = widgets.TextField('name', default=0)
    assert textfield.default == 0
    output = textfield.render(format='xhtml')
    assert 'value="0"' in output
    textfield = widgets.TextField('name', default='')
    assert textfield.default == ''
    output = textfield.render(format='xhtml')
    assert 'value=""' in output
    msfield = widgets.MultipleSelectField(
        'name', default=[], options=(1, 2, 3))
    assert msfield.default == []
    output = msfield.render(format='xhtml')
    assert 'selected' not in output


def test_labeltext():
    """Label text defaults to the capitalized name"""
    textfield = widgets.TextField('name')
    assert textfield.label == 'Name'

def test_validation():
    """Values can be converted to/from Python values"""
    textfield = widgets.TextField('age', validator=validators.Int())
    output = textfield.render(2, format='xhtml')
    assert 'value="2"' in output
    value = "2"
    value = textfield.validator.to_python(value)
    assert value == 2


def test_unicode_input():
    """Unicode values are rendered correctly"""
    tf = widgets.TextField('name', validator=validators.String())
    output = tf.render(u'Pete \u011C', format='xhtml')
    assert 'value="Pete \xc4\x9c"' in output
    try:
        tf.render('Pete \xfe\xcd')
    except ValueError:
        pass
    else:
        assert False, "ValueError not raised: non-unicode input not detected"
    tf = widgets.TextField('name', validator=validators.UnicodeString())
    output = tf.render(u'Pete \u011C', format='xhtml')
    assert 'value="Pete \xc4\x9c"' in output
    try:
        tf.render('Pete \xfe\xcd')
    except ValueError:
        pass
    else:
        assert False, "ValueError not raised: non-unicode input not detected"


def test_failed_validation():
    """If validation fails, the bad value should be removed from the input"""
    textfield = widgets.TextField('age', validator=validators.Int())
    values = dict(age='ed')
    try:
        textfield.validator.to_python(values)
    except validators.Invalid:
        pass
    # failed inputs are no longer being removed
    assert values.get('age') == 'ed'


def test_widget_css():
    """Widgets can require CSS resources"""
    css = widgets.CSSLink(mod=widgets.static, name='foo.css')
    css2 = widgets.CSSLink(mod=widgets.static, name='foo.css')
    assert css == css2
    cssset = set()
    cssset.add(css)
    cssset.add(css2)
    assert len(cssset) == 1
    css3 = widgets.CSSLink(mod=widgets.static, name='bar.css')
    assert css3 != css2
    css4 = widgets.CSSSource(src='foo.css')
    assert css != css4
    rendered = css.render(format='xhtml')
    assert 'link' in rendered
    assert 'href="/tg_widgets/turbogears.widgets/foo.css"' in rendered
    assert 'type="text/css"' in rendered
    assert 'rel="stylesheet"' in rendered
    assert 'media="all"' in rendered
    rendered = css.render(media="printer", format='xhtml')
    assert 'media="printer"' in rendered
    css = widgets.CSSSource("h1 { color: black }")
    rendered = css.render(format='xhtml')
    assert 'h1 { color: black }' in rendered


def test_widget_js():
    """Widgets can require JavaScript resources"""
    js = widgets.JSLink(mod=widgets.static, name='foo.js')
    js2 = widgets.JSLink(mod=widgets.static, name='foo.js')
    assert js2 == js2
    js2 = widgets.JSLink(mod=widgets.static, name='bar.js')
    assert js2 != js
    js2 = widgets.CSSLink(mod=widgets.static, name='foo.js')
    assert js2 != js
    js2 = widgets.JSSource(src='foo.js')
    assert js2 != js
    rendered = js.render(format='xhtml')
    expected = ('<script ', ' src="/tg_widgets/turbogears.widgets/foo.js"',
        ' type="text/javascript"', '></script>')
    assert rendered.startswith(expected[0]) and rendered.endswith(expected[3])
    assert expected[1] in rendered and expected[2] in rendered
    js3 = widgets.JSLink(mod=widgets.static, name='foo.js',
        defer=False, charset=None)
    assert js3 == js
    rendered = js3.render(format='xhtml')
    assert rendered.startswith(expected[0]) and rendered.endswith(expected[3])
    assert expected[1] in rendered and expected[2] in rendered
    js3 = widgets.JSLink(mod=widgets.static, name='foo.js', defer=True)
    assert js3 != js
    rendered = js3.render(format='html').lower()
    assert ' defer' in rendered
    assert rendered.startswith(expected[0]) and rendered.endswith(expected[3])
    assert expected[1] in rendered and expected[2] in rendered
    rendered = js3.render(format='xhtml')
    assert ' defer="defer"' in rendered
    assert rendered.startswith(expected[0]) and rendered.endswith(expected[3])
    assert expected[1] in rendered and expected[2] in rendered
    js3 = widgets.JSLink(mod=widgets.static, name='foo.js', charset='Latin-1')
    assert js3 != js
    rendered = js3.render(format='xhtml')
    assert ' charset="Latin-1"' in rendered
    assert rendered.startswith(expected[0]) and rendered.endswith(expected[3])
    assert expected[1] in rendered and expected[2] in rendered
    js3 = widgets.JSSource("alert('hello');")
    assert js3 != js and js3 != js2
    rendered = js3.render(format='xhtml')
    expected = '<script type="text/javascript">alert(\'hello\');</script>'
    assert rendered == expected
    js4 = widgets.JSSource("alert('hello');", defer=False)
    assert js4 == js3
    rendered = js4.render(format='xhtml')
    assert rendered == expected
    js4 = widgets.JSSource("alert('hello');", defer=True)
    assert js4 != js3
    rendered = js4.render(format='html').lower()
    assert ' defer' in rendered
    rendered = rendered.replace(' defer', '', 1)
    assert rendered == expected
    rendered = js4.render(format='xhtml')
    assert ' defer="defer"' in rendered
    rendered = rendered.replace(' defer="defer"', '', 1)
    assert rendered == expected


def test_widgetslist_init():
    """Widget lists can be declared in various ways."""
    if has_trace_bug:
        return # skip to avoid false-negative

    w = widgets.Widget(name='foo')
    widgetlist = widgets.WidgetsList(w)
    assert len(widgetlist) == 1
    assert widgetlist[0] == w
    widgetlist = widgets.WidgetsList([w])
    assert len(widgetlist) == 1
    assert widgetlist[0] == w
    w2 = widgets.Widget(name='bar')
    widgetlist = widgets.WidgetsList(w, w2)
    assert len(widgetlist) == 2
    assert widgetlist[0] == w
    assert widgetlist[1] == w2
    widgetlist = widgets.WidgetsList([w, w2])
    assert len(widgetlist) == 2
    assert widgetlist[0] == w
    assert widgetlist[1] == w2

    class W(widgets.WidgetsList):
        foo = w
        bar = w2

    widgetlist = W()
    assert len(widgetlist) == 2
    assert widgetlist[0] == w
    assert widgetlist[1] == w2
    w3, w4 = widgets.Widget(), widgets.Widget()
    widgetlist = W([w3, w4])
    assert len(widgetlist) == 4
    assert widgetlist[0] == w
    assert widgetlist[1] == w2
    assert widgetlist[2] == w3
    assert widgetlist[3] == w4


def test_widgetslist_inheritance():
    """Widget lists can inherit fields."""
    if has_trace_bug:
        return # skip to avoid false-negative

    w = widgets.Widget(name='foo')

    class W(widgets.WidgetsList):
        foo = w

    w2 = widgets.Widget(name='bar')

    class W2(W):
        bar = w2

    widgetlist = W2()
    assert len(widgetlist) == 2
    assert widgetlist[0] == w
    assert widgetlist[1] == w2
    w3, w4 = widgets.Widget(), widgets.Widget()
    widgetlist = W2([w3, w4])
    assert len(widgetlist) == 4
    assert widgetlist[0] == w
    assert widgetlist[1] == w2
    assert widgetlist[2] == w3
    assert widgetlist[3] == w4


def test_declared_widgets_stay_as_attrs():
    """Ensure declared attributes of widget lists are not removed."""

    class W1(widgets.WidgetsList):
        foo = widgets.Widget()

    w1 = W1()
    assert len(w1) == 1
    assert w1[0].name == 'foo'
    assert hasattr(w1, 'foo'), (
        'Declared widgets should be kept accessible as attribute')
    assert w1.foo.name == 'foo'

    class W2(W1):
        bar = widgets.Widget()

    w2 = W2()
    assert len(w2) == 2
    assert w2[0].name == 'foo'
    assert w2[1].name == 'bar'
    assert hasattr(w2, 'foo')
    assert hasattr(w2, 'bar')
    assert w2.foo.name == 'foo'
    assert w2.bar.name == 'bar'

    class W3(widgets.WidgetsList):
        pass

    w3 = W3(widgets.Widget(name='foo'))

    assert len(w3) == 1
    assert w3[0].name == 'foo'
    assert not hasattr(w3, 'foo'), (
        'Only declared widgets should be accessible as attribute')


def test_widget_url():
    """It might be needed to insert an URL somewhere"""
    url = widgets.URLLink(link='http://www.turbogears.org')
    rendered = url.render(format='xhtml')
    expected = '<a href="http://www.turbogears.org"></a>'
    assert rendered == expected
    url = widgets.URLLink(link='http://www.turbogears.org',
        text='TurboGears Website')
    rendered = url.render(format='xhtml')
    expected = """<a href="http://www.turbogears.org">TurboGears Website</a>"""
    assert rendered == expected
    url = widgets.URLLink(link='http://www.turbogears.org',
        text='TurboGears Website', target='_blank')
    rendered = url.render(format='xhtml')
    expected = ('<a href="http://www.turbogears.org" target="_blank">'
        'TurboGears Website</a>')
    assert rendered == expected


def test_submit():
    sb = widgets.SubmitButton()
    r = sb.render(format='xhtml')
    assert 'name' not in r
    assert 'id' not in r
    r = sb.render('Krakatoa', format='xhtml')
    assert 'id' not in r
    assert 'name' not in r
    sb = widgets.SubmitButton(name='blink')
    r = sb.render(format='xhtml')
    assert 'name="blink"' in r
    assert 'id="blink"' in r
    r = sb.render('Krakatoa', format='xhtml')
    assert 'name="blink"' in r
    assert 'id="blink"' in r
    sb = widgets.SubmitButton(name='submit')
    r = sb.render(format='xhtml')
    assert 'name="submit"' in r
    assert 'id="submit"' in r
    r = sb.render('Krakatoa', format='xhtml')
    assert 'name="submit"' in r
    assert 'id="submit"' in r
    sb = widgets.SubmitButton(default='Save')
    r = sb.render(format='xhtml')
    assert 'value="Save"' in r
    r = sb.render(value='Discard', format='xhtml')
    assert 'value="Discard"' in r


def test_threadsafety():
    """Widget attributes can't be changed after init, for threadsafety"""
    w = widgets.TextField('bar')
    w.display()
    try:
        w.name = 'foo'
        assert False, "should have gotten an exception"
    except ValueError:
        pass


def test_same_classname():
    """Check that two widgets can have the same classname (#2443)."""

    # Note that a potential problem exists only for Kid templates,
    # for which the template module name had been constructed from the
    # module and class name of the widget (which must not be unique).

    class W(widgets.Widget):
        template = 'kid:<w1/>'

    w1 = W()

    class W(widgets.Widget):
        template = 'kid:<w2/>'

    w2 = W()

    try:
        r = w1.render()
    except Exception, e:
        r = 'Rendering Error: %s' % e
    assert r == '<w1></w1>', r

    try:
        r = w2.render()
    except Exception, e:
        r = 'Rendering Error: %s' % e
    assert r == '<w2></w2>', r


def test_checkbox():
    """A CheckBox has not a value and is not checked by default"""
    w = widgets.CheckBox('foo')
    output = w.render(format='xhtml')
    assert 'name="foo"' in output
    assert 'value' not in output
    assert 'checked' not in output
    output = w.render(value=True, format='xhtml')
    assert 'checked' in output
    w = widgets.CheckBox('foo', default=True)
    output = w.render(format='xhtml')
    assert 'checked' in output
    output = w.render(value=False, format='xhtml')
    assert 'checked' not in output
    #CheckBox should accept alternate validators
    value = w.validator.to_python('checked')
    assert value == True
    w = widgets.CheckBox('foo', validator=validators.NotEmpty())
    value = w.validator.to_python('checked')
    assert value == 'checked'


def test_field_class():
    """The class of a field corresponds to the name of its Python class"""
    w = widgets.TextField('bar')
    output = w.render(format='xhtml')
    assert 'class="%s"' % w.__class__.__name__.lower() in output


def test_field_id():
    """The id of a field corresponds to the name of the field"""
    w = widgets.TextField('bar')
    output = w.render(format='xhtml')
    assert 'id="bar"' in output


def test_override_name():
    """The name of a widget can be overridden when displayed"""
    w = widgets.DataGrid(name="bar", fields=[])
    output = w.render([], name='foo', format='xhtml')
    assert 'id="foo"' in output


def test_selection_field():
    """A selection field presents a list of options that can be changed
    dynamically. One or more options can be selected/checked by default
    or dynamically."""
    options = [(1, 'python'), (2, 'java'), (3, 'pascal')]
    w = widgets.SingleSelectField(options=options)
    output = w.render(format='xhtml')
    assert 'python' in output
    assert 'java' in output
    assert 'pascal' in output
    output = w.render(value=2, format='xhtml')
    assert '<option value="1">' in output
    assert ('<option selected="selected" value="2">' in output
        or '<option value="2" selected="selected">' in output)
    assert '<option value="3">' in output
    w = widgets.SingleSelectField(options=options, default=3)
    output = w.render(format='xhtml')
    assert '<option value="1">' in output
    assert '<option value="2">' in output
    assert ('<option selected="selected" value="3">' in output
        or '<option value="3" selected="selected">' in output)
    output = w.render(options=options + [(4, 'cobol'), (5, 'ruby')],
        format='xhtml')
    assert 'python' in output
    assert 'java' in output
    assert 'pascal' in output
    assert 'cobol' in output
    assert 'ruby' in output
    output = w.render(options=options
        + [(4, 'cobol'), (5, 'ruby')], value=5, format='xhtml')
    assert '<option value="1">' in output
    assert '<option value="2">' in output
    assert '<option value="3">' in output
    assert '<option value="4">' in output
    assert ('<option selected="selected" value="5">' in output
        or '<option value="5" selected="selected">' in output)
    w = widgets.MultipleSelectField(options=options, default=[1, 3])
    output = w.render(format='xhtml')
    assert ('<option selected="selected" value="1">' in output
        or '<option value="1" selected="selected">' in output)
    assert '<option value="2">' in output
    assert ('<option selected="selected" value="3">' in output
        or '<option value="3" selected="selected">' in output)
    output = w.render(options=options
        + [(4, 'cobol'), (5, 'ruby')], value=[2, 4, 5], format='xhtml')
    assert '<option value="1">' in output
    assert ('<option selected="selected" value="2">' in output
        or '<option value="2" selected="selected">' in output)
    assert '<option value="3">' in output
    assert ('<option selected="selected" value="4">' in output
        or '<option value="4" selected="selected">' in output)
    assert ('<option selected="selected" value="5">' in output
        or '<option value="5" selected="selected">' in output)


def test_callable_options():
    """Widgets support callable options passed to the
    constructor or dynamically"""

    def options_func1():
        return [(1, 'coke'), (2, 'pepsi'), (3, 'redbull')]

    def options_func2():
        return [(1, 'python'), (2, 'java'), (3, 'pascal')]

    w = widgets.SingleSelectField(options=options_func1)
    output = w.render(format='xhtml')
    assert 'coke' in output
    assert 'pepsi' in output
    assert 'redbull' in output
    output = w.render(options=options_func2, format='xhtml')
    assert 'coke' not in output
    assert 'pepsi' not in output
    assert 'redbull' not in output
    assert 'python' in output
    assert 'java' in output
    assert 'pascal' in output


def test_selection_field_converted_value():
    """Verify that values are properly converted when rendering selection
    fields with validators"""

    class TestValue:

        def __init__(self, value):
            self.value = value

        def __eq__(self, other):
            if isinstance(other, TestValue):
                return self.value == other.value
            else:
                return False

        def __hash__(self):
            return hash(self.value)

    class TestValidator:

        def to_python(self, value, state=None):
            try:
                value = int(value)
                if not 0 < value < 5:
                    raise ValueError
            except ValueError:
                raise validators.Invalid('Bad Value', value, state)
            return TestValue(value)

        def from_python(self, value, state=None):
            return str(value.value)

    # Test SingleSelectField
    single = widgets.SingleSelectField(
        'testval', options=[
            (TestValue(1), 'one'), (TestValue(2), 'two'),
            (TestValue(3), 'three'), (TestValue(4), 'four')],
        validator=TestValidator())
    output = single.render(format='xhtml')
    assert ('<option value="1">one</option><option value="2">two</option>'
        '<option value="3">three</option>'
        '<option value="4">four</option>') in output, output
    assert single.render(None, format='xhtml') == output
    assert single.render('', format='xhtml') == output
    output = single.render(TestValue(3), format='xhtml')
    selected = output.replace('selected="selected"', '*')
    selected = selected.replace('value="3" *', '* value="3"')
    assert ('<option value="1">one</option><option value="2">two</option>'
        '<option * value="3">three</option>'
        '<option value="4">four</option>') in selected, output
    assert single.render(u'3', format='xhtml') == output
    # Test MultipleSelectField
    multiple = widgets.MultipleSelectField(
        'testval', options=[(TestValue(1), 'one'), (TestValue(2), 'two'),
            (TestValue(3), 'three'), (TestValue(4), 'four')],
        validator=validators.ForEach(TestValidator()))
    output = multiple.render(format='xhtml')
    assert ('<option value="1">one</option>'
        '<option value="2">two</option>'
        '<option value="3">three</option>'
        '<option value="4">four</option>' in output), output
    assert multiple.render(None, format='xhtml') == output
    assert multiple.render('', format='xhtml') == output
    assert multiple.render([], format='xhtml') == output
    assert multiple.render(set(), format='xhtml') == output
    output = multiple.render([TestValue(3)], format='xhtml')
    selected = output.replace('selected="selected"', '*')
    selected = selected.replace('value="3" *', '* value="3"')
    assert ('<option value="1">one</option>'
        '<option value="2">two</option>'
        '<option * value="3">three</option>'
        '<option value="4">four</option>' in selected), output
    assert multiple.render(set([TestValue(3)]), format='xhtml') == output
    assert multiple.render(u'3', format='xhtml') == output
    output = multiple.render([TestValue(1), TestValue(3)], format='xhtml')
    selected = output.replace('selected="selected"', '*')
    selected = selected.replace('value="1" *', '* value="1"')
    selected = selected.replace('value="3" *', '* value="3"')
    assert ('<option * value="1">one</option>'
        '<option value="2">two</option>'
        '<option * value="3">three</option>'
        '<option value="4">four</option>' in selected), output
    assert multiple.render(
        set([TestValue(1), TestValue(3)]), format='xhtml') == output
    assert multiple.render([u'1', u'3'], format='xhtml') == output
    assert multiple.render(set([u'1', u'3']), format='xhtml') == output


def test_empty_selection_field():
    """Check that the section field value can be empty."""
    single = widgets.SingleSelectField(
        'testval', options=[
            (None, 'undefined'), (1, 'one'), (2, 'two'), (3, 'three')],
        validator=validators.Int())
    output = single.render(format='xhtml')
    output = output.replace('selected="selected"', '*')
    output = output.replace('value="" *', '* value=""')
    assert '<option * value="">undefined</option>' in output
    assert '<option value="2">two</option>' in output
    output = single.render(2, format='xhtml')
    output = output.replace('selected="selected"', '*')
    output = output.replace('value="2" *', '* value="2"')
    assert '<option value="">undefined</option>' in output
    assert '<option * value="2">two</option>' in output
    multiple = widgets.MultipleSelectField(
        'testval', options=[
            (None, 'undefined'), (1, 'one'), (2, 'two'), (3, 'three')],
        validator=validators.Int())
    output = multiple.render(format='xhtml')
    assert '<option value="">undefined</option>' in output
    assert '<option value="2">two</option>' in output
    output = multiple.render([None], format='xhtml')
    output = output.replace('selected="selected"', '*')
    output = output.replace('value="" *', '* value=""')
    assert '<option * value="">undefined</option>' in output
    assert '<option value="2">two</option>' in output
    output = multiple.render([2], format='xhtml')
    output = output.replace('selected="selected"', '*')
    output = output.replace('value="2" *', '* value="2"')
    assert '<option value="">undefined</option>' in output
    assert '<option * value="2">two</option>' in output
    output = multiple.render([None, 2], format='xhtml')
    output = output.replace('selected="selected"', '*')
    output = output.replace('value="" *', '* value=""')
    output = output.replace('value="2" *', '* value="2"')
    assert '<option * value="">undefined</option>' in output
    assert '<option * value="2">two</option>' in output
    output = multiple.render([1, 3], format='xhtml')
    output = output.replace('selected="selected"', '*')
    output = output.replace('value="1" *', '* value="1"')
    output = output.replace('value="3" *', '* value="3"')
    assert '<option value="">undefined</option>' in output
    assert '<option * value="1">one</option>' in output
    assert '<option value="2">two</option>' in output
    assert '<option * value="3">three</option>' in output


class TestParams:

    class A(widgets.Widget):
        template = """<tag xmlns:py="http://genshi.edgewall.org/" a="${a}" />"""
        params = ["a", "b", "c"]

    class B(widgets.Widget):
        params = ["b", "c", "d"]

    class C(A, B):
        params = ["c", "d", "e"]

    def test_building_params(self):
        """Test that the list of params is built correctly.

        Must be the union of all params from all bases.

        """
        # for easy equivalenece testing
        self.C.params.sort()
        assert ''.join(self.C.params) == "abcde"

    def test_default_values(self):
        """Test that undeclared params default to None.

        Check that params which are not initialized at the constructor
        or at the subclass declaration default to None.

        """
        a = self.A()
        assert a.a is None
        output = a.render(format='xhtml')
        assert 'a=' not in output

    def test_overridal(self):
        """Test that template variables can be overridden.

        Check that we can override a template_var in the constructor
        and at display time. Both from the class and its bases.

        """
        a = self.A(a='test')
        assert a.a == 'test'
        c = self.C(a='test')
        assert c.a == 'test'
        output = c.render(format='xhtml')
        assert 'a="test"' in output
        output = c.render(a="another", format='xhtml')
        assert 'a="another"' in output


def test_template_overridal():
    """Test that the template can be overridden.

    Check that we can override the template of a widget
    at construction time and get it automatically compiled.

    """
    new_template = """
    <label xmlns:py="http://genshi.edgewall.org/"
        for="${name}"
        class="${field_class}"
        py:content="value"
        custom_template="True"
    />
    """
    label = widgets.Label(template=new_template)
    output = label.render('custom', format='xhtml')
    assert '<label ' in output
    assert 'xmlns:py' not in output
    assert '>custom</label>' in output
    assert 'custom_template="True"' in output


def test_engine_overridal():
    """Test that the templating engine can be overridden.

    Check that we can override the templating engine for a widget
    at construction time and get the template automatically compiled.

    """
    new_template = """
    <label xmlns:py="http://purl.org/kid/ns#"
        for="${name}"
        class="${field_class}"
        py:content="value"
        custom_template="True"
        custom_engine="kid"
    />
    """
    label = widgets.Label(template=new_template)
    assert label.engine_name == 'genshi'
    output = label.render('custom', format='xhtml')
    assert 'xmlns:py' in output # Kid template doesn't work with Genshi
    label = widgets.Label(template=new_template, engine_name='kid')
    output = label.render('custom', format='xhtml')
    assert '<label ' in output
    assert 'xmlns:py' not in output
    assert '>custom</label>' in output
    assert 'custom_template="True"' in output
    assert 'custom_engine="kid"' in output
    label = widgets.Label(template='kid:' + new_template)
    output = label.render('custom', format='xhtml')
    assert '<label ' in output
    assert 'xmlns:py' not in output
    assert '>custom</label>' in output
    assert 'custom_template="True"' in output
    assert 'custom_engine="kid"' in output


def test_simple_widget_attrs():
    """Test attributes of simple widget.

    A simple widget supports attributes passed to the constructor
    or at display time.

    """
    w = widgets.TextField(name="foo", attrs=dict(onchange='python', size='10'))
    output = w.render(format='xhtml')
    assert 'onchange="python"' in output
    assert 'size="10"' in output
    output = w.render(attrs=dict(onclick='java'), format='xhtml')
    assert 'onchange="python"' not in output
    assert 'size="10"' not in output
    assert 'onclick="java"' in output
    output = w.render(attrs=dict(onchange='java', size='50', alt=None),
        format='xhtml')
    assert 'onchange="java"' in output
    assert 'size="50"' in output
    assert 'alt' not in output
    assert 'onclick' not in output


def test_textfield():
    """Test form rendering inside a request."""

    # form name is prepended to element ids only when running inside a request.

    class MyField(widgets.WidgetsList):
        blonk = widgets.TextField()

    tf = widgets.ListForm(fields=MyField())

    class MyFieldOverrideName(widgets.WidgetsList):
        blonk = widgets.TextField(name='blink')

    tf2 = widgets.ListForm(fields=MyFieldOverrideName())

    class MyRoot(controllers.RootController):

        @expose()
        def fields(self):
            return tf.render(format='xhtml')

        @expose()
        def override(self):
            return tf2.render(format='xhtml')

    testutil.mount(MyRoot(), '/')
    app = testutil.make_app()
    r = app.get('/fields')
    assert 'name="blonk"' in r
    assert 'id="form_blonk"' in r

    r = app.get('/override')
    assert 'name="blink"' in r
    assert 'id="form_blink"' in r


def test_textarea():
    w = widgets.TextArea(rows=20, cols=30)
    output = w.render(format='xhtml')
    assert 'rows="20"' in output
    assert 'cols="30"' in output
    output = w.render(rows=50, cols=50, format='xhtml')
    assert 'rows="50"' in output
    assert 'cols="50"' in output
    assert '> +++ </textarea>' in w.render(' +++ ', format='xhtml')


def test_render_field_for():
    """Test the render_field_for() method.

    Using the render_field_for method of a FormFieldsContainer we can
    render the widget instance associated to a particular field name.

    """

    class MyFields(widgets.WidgetsList):
        name = widgets.TextField()
        age = widgets.TextArea()

    tf = widgets.ListForm(fields=MyFields())
    output = tf.render_field_for('name', format='xhtml')
    assert 'name="name"' in output
    assert '<input' in output
    assert 'type="text"' in output
    output = tf.render_field_for('name', attrs={'onclick':'hello'},
        format='xhtml')
    assert 'onclick="hello"' in output
    output = tf.render_field_for('age', format='xhtml')
    assert 'name="age"' in output
    assert '<textarea' in output
    output = tf.render_field_for('age', rows="1000", cols="2000",
        format='xhtml')
    assert 'rows="1000"' in output
    assert 'cols="2000"' in output


def test_css_classes():
    """Test CSS classes support.

    A FormField supports css_classes; they are added after the original
    class. They can be provided at construction or at display time,
    the latter overrides the former but attrs overrides everything.

    """
    w = widgets.TextField(name='foo')
    output = w.render(format='xhtml')
    assert 'class="textfield"' in output
    w = widgets.TextField(name="foo", css_classes=['bar', 'bye'])
    output = w.render(format='xhtml')
    assert 'class="textfield bar bye"' in output
    output = w.render(css_classes=["coke", "pepsi"], format='xhtml')
    assert 'class="textfield coke pepsi"' in output
    w = widgets.TextField(name='foo',
        css_classes=['bar', 'bye'], attrs={'class': 'again'})
    output = w.render(format='xhtml')
    assert 'class="again"' in output
    output = w.render(css_classes=['coke', 'pepsi'], format='xhtml')
    assert 'class="again"' in output
    output = w.render(css_classes=['coke', 'pepsi'],
        attrs={'class': 'funny'}, format='xhtml')
    assert 'class="funny"' in output


def test_ticket272():
    """TextFields with a "name" attribute = "title" should be OK."""
    w = widgets.TableForm(fields=[widgets.TextField(name='title')])
    output = w.render(format='xhtml')
    assert 'value' not in output


class TestSchemaValidation:
    """Test schema validation.

    Tests the validation of a CompoundWidget is done correctly with a
    Schema validator and no validators on the child widgets.

    """

    class Fields(widgets.WidgetsList):
        name = widgets.TextField()
        age = widgets.TextField()
        passwd = widgets.PasswordField()
        passwd2 = widgets.PasswordField()

    class FieldsSchema(validators.Schema):
        chained_validators = [validators.FieldsMatch('passwd', 'passwd2')]
        name = validators.UnicodeString()
        age = validators.Int()
        passwd = validators.NotEmpty()
        passwd2 = validators.UnicodeString()

    form = widgets.TableForm(fields=Fields(), validator=FieldsSchema())

    def test_goodvalues(self):
        values = dict(name=u'Jos\xc3\xa9', age='99',
            passwd='fado', passwd2='fado')
        values, errors = catch_validation_errors(self.form, values)
        assert values['age'] == 99
        assert not errors

    def test_badvalues(self):
        values = dict(name=u'Jos\xc3\xa9', age='99',
            passwd='fado', passwd2='fadO')
        values, errors = catch_validation_errors(self.form, values)
        assert 'passwd2' in errors


class TestSchemaValidationWithChildWidgetsValidators:
    """Test schema validation with child widgets validators.

    Tests the validation of a CompoundWidget is done correctly with a schema
    validator and independent validators on the each of the child widgets.

    """

    class Fields(widgets.WidgetsList):
        name = widgets.TextField(validator = validators.UnicodeString())
        age = widgets.TextField(validator = validators.Int())
        passwd = widgets.PasswordField(validator = validators.NotEmpty())
        passwd2 = widgets.PasswordField(validator = validators.UnicodeString())

    class FieldsSchema(validators.Schema):
        chained_validators = [validators.FieldsMatch('passwd', 'passwd2')]

    form = widgets.TableForm(fields=Fields(), validator=FieldsSchema())

    def test_goodvalues(self):
        values = dict(name=u'Jos\xc3\xa9', age='99',
            passwd='fado', passwd2='fado')
        values, errors = catch_validation_errors(self.form, values)
        assert values['age'] == 99
        assert not errors

    def test_widget_validator_failure(self):
        values = dict(name=u'Jos\xc3\xa9', age='ninetynine',
            passwd='fado', passwd2='fado')
        values, errors = catch_validation_errors(self.form, values)
        assert 'age' in errors

    def test_widget_validator_and_schema_failure(self):
        values = dict(name=u'Jos\xc3\xa9', age='ninetynine',
            passwd='fado', passwd2='fadO')
        values, errors = catch_validation_errors(self.form, values)
        assert 'age' in errors
        assert 'passwd2' in errors


def test_param_descriptor():

    class Base(widgets.Widget):
        params = ['param1', 'param2']
        param1 = 'original'
        param2 = 'original'

    class Sub(Base):
        param1 = lambda self: 'overrided'
        param2 = 'overrided'

    base = Base()
    assert base.param1 == 'original', "descriptor is not created correctly"
    assert base.param2 == 'original', "descriptor is not created correctly"

    sub = Sub()
    assert sub.param1 == 'overrided', "callable params are not being overrided"
    assert sub.param2 == 'overrided', "normal params are not being overrided"


def test_param_descriptor_mutable_class_attrs():

    class W(widgets.Widget):
        params = ['attrs']
        attrs = {}

    w1 = W(attrs={'test':True})
    w2 = W()

    assert w1.attrs == {'test':True}
    assert w2.attrs == {}


def test_lazy_param_initialization():
    """Test lazy initialization of widget parameters."""

    class Widget(widgets.Widget):
        params = ['test']
        touched = False
        def test(self):
            self.touched = True

    w = Widget()
    assert not w.touched, 'Widget.test param must not be touched automatically!'


def test_param_without_declaration():
    """Test widget parameters without explicit initialization."""

    class W(widgets.Widget):
        params = ['test']

    w = W()
    assert w.test is None, w.test

    class W(widgets.Widget):
        params = ['test']

    w = W(test=lambda: 42)
    assert w.test == 42, w.test

    class W(widgets.Widget):
        params = ['test']

    w = W()
    w.test = lambda: 42
    assert w.test == 42,  w.test


def test_param_descriptor_properties():

    class W(widgets.Widget):

        params = ['attrs']

        def _set_attrs(self, attrs):
            self._attrs = attrs

        def _get_attrs(self):
            return self._attrs

        attrs = property(_get_attrs, _set_attrs)

    w1 = W(attrs=dict(test=True))
    assert w1.attrs == dict(test=True)


def test_dict_as_validator():

    class Foo(widgets.InputWidget):
        validator = validators.Int()

    a = Foo()
    b = Foo(validator=dict(not_empty=True))
    assert not a.validator.not_empty
    assert b.validator.not_empty
    assert a.validator is not b.validator


def test_params_doc():
    """Test params documentation.

    Tests params_doc are picked from all bases
    giving priority to the widget's own params_docs.

    """

    class A(widgets.Widget):
        params_doc = dict(a=1)

    class B(widgets.Widget):
        params_doc = dict(b=2)

    class C(A, B):
        params_doc = dict(c=3, a=4)

    w = C()
    assert w.params_doc == dict(a=4, b=2, c=3)


def test_selectfield_with_with_non_iterable_option_elements():
    options = ['python', 'java', 'pascal']
    w = widgets.SingleSelectField(options=options)
    output = w.render(format='xhtml')
    assert '<option value="python">' in output
    assert '<option value="java">' in output
    assert '<option value="pascal">' in output
    output = w.render(value="python", format='xhtml')
    assert ('<option selected="selected" value="python">' in output
        or '<option value="python" selected="selected">' in output)
    assert '<option value="java">' in output
    assert '<option value="pascal">' in output


def test_calendardatepicker():
    """Test calendar date picker.

    Tests that the CalendarDatePicker widget is wrapped in a span element
    with the proper class.

    """
    w = widgets.CalendarDatePicker(
       name='test_cdp',
       field_class='my_cdp',
       label='Test',
       format='%m/%d/%Y',
       validator=validators.DateConverter(format='mm/dd/yyyy'))
    output = w.render(format='xhtml')
    assert '<span class="my_cdp">' in output


def test_calendardatetimepicker():
    """Test calendar date time picker.

    Tests that the CalendarDateTimePicker widget is wrapped in a span element
    with the proper class.

    """
    w = widgets.CalendarDateTimePicker(
       name='test_cdp',
       field_class='cdp',
       label='Test',
       format='%m/%d/%Y',
       validator=validators.DateConverter(format='mm/dd/yyyy'))
    output = w.render(format='xhtml')
    assert '<span class="cdp">' in output


def test_autocompletefield():
    """Test auto complete field widget.

    Tests that the AutoCompleteField widget is wrapped in a span element
    with the proper class/id.

    """
    w = widgets.AutoCompleteField(name='my_acf',
        field_class='acf',
        search_controller='/search',
        search_param='test', result_name='test')
    output = w.render(format='xhtml')
    assert '<span id="my_acf" class="acf">' in output


def test_autocompletetextfield():
    """Test auto complete text field widget.

    Tests that the AutoCompleteTextField widget is wrapped in a span element
    with the proper class/id.

    """
    w = widgets.AutoCompleteTextField(name="my_actf",
        field_class='actf',
        search_controller='/search',
        search_param='test', result_name='test')
    output = w.render(format='xhtml')
    assert '<span class="actf">' in output


def test_jsi18nwidget():
    """JSI18NWidget includes all needed Javascript files."""
    get_locale = config.get('i18n.get_locale')
    config.update({'i18n.get_locale': lambda: 'ru'})
    exists = os.path.exists
    os.path.exists = lambda path: (
        os.path.split(path)[1] == 'messages-ru.js' or exists(path))
    try:
        js = widgets.jsi18nwidget.retrieve_javascript()
    finally:
        os.path.exists = exists
        config.update({'i18n.get_locale': get_locale})
    assert len(js) == 2
    assert js[0].name == 'js/i18n_base.js'
    assert js[1].name == 'messages-ru.js'
