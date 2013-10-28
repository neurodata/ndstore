#!/usr/bin/python
# -*- coding: utf-8 -*-

from cherrypy import request

from turbogears import (config, controllers, expose, testutil,
    validate, validators, widgets)
from turbogears.testutil import catch_validation_errors, make_app


def setup_module():
    testutil.start_server()


def teardown_module():
    testutil.stop_server()


def test_rendering():
    """Forms can be rendered"""
    for Form in (widgets.TableForm, widgets.ListForm):
        form = Form(
            fields=[widgets.TextField("name", label="Your Name")])
        output = form.render(action="mylocation", format="xhtml")
        assert '<form ' in output and '</form>' in output
        assert 'action="mylocation"' in output
        assert 'method="post"' in output
        assert 'id="form"' in output
        assert 'name="form"' not in output
        assert "Your Name" in output
        assert 'name="name"' in output
        assert "submit" in output
        assert (Form is widgets.TableForm) == (
            '</table>' in output and '</td>' in output)
        assert (Form is widgets.ListForm) == (
            '</ul>' in output and '</li>' in output)
        form = Form(name="myform",
            fields=[widgets.TextField("myfield")])
        output = form.render(format="xhtml")
        assert 'name="myform"' not in output
        assert 'id="myform"' in output
        assert 'name="myfield"' in output
        form = Form(name="myform", use_name=True,
            fields=[widgets.TextField("myfield")])
        output = form.render(format="xhtml")
        assert 'name="myform"' in output
        assert 'id="myform"' not in output
        assert 'name="myfield"' in output


def test_input_conversion():
    """Input for the whole form can be validated and converted"""
    form = widgets.TableForm(fields=[widgets.TextField('name'),
        widgets.TextField('age', validator=validators.Int())],
        submit_text='Submit')
    values = dict(name='ed', age='15')
    values = form.validate(values)
    assert values['name'] == 'ed'
    assert values['age'] == 15
    assert 'submit' not in values


def test_passing_instance():
    """You can pass an instance to a form for the value"""
    form = widgets.TableForm(fields=[widgets.TextField('name'),
        widgets.TextField('age', validator=validators.Int())],
        submit_text='Submit')
    class Person(object):
        name = 'ed'
        age = 892
    output = form.render(Person(), format='xhtml')
    assert 'value="ed"' in output
    assert 'value="892"' in output


def test_input_errors():
    """Data is stored in the request object if there are errors"""
    form = widgets.TableForm(fields=[widgets.TextField('name'),
        widgets.TextField('age', validator=validators.Int())])
    values = dict(name='ed', age='ed')
    values, errors = catch_validation_errors(form, values)
    assert "enter an integer" in str(errors['age'])


class w1(widgets.FormField):

    javascript = [widgets.JSLink(__module__, 'foo.js'),
        widgets.JSSource("alert('foo');"),
        widgets.JSSource("alert('foo again');",
            widgets.js_location.bodybottom)]
    css = [widgets.CSSLink(__module__, 'foo.css')]
    register = False


class w2(widgets.FormField):

    javascript = [widgets.JSLink(__module__, 'foo.js')]
    css = [widgets.CSSLink(__module__, 'foo.css')]
    register = False


def test_javascriptsets():
    """JavaScripts are only added once"""
    form = widgets.TableForm(fields=[w1('foo'), w2('bar')])
    assert len(form.retrieve_javascript()) == 3


def test_csssets():
    """CSS references are added once"""
    form = widgets.TableForm(fields=[w1('foo'), w2('bar')])
    assert len(form.retrieve_css()) == 1


def test_creation():

    class TestFormFields(widgets.WidgetsList):
        foo = widgets.TextField()
        bar = widgets.CheckBox()

    t = widgets.TableForm(fields=TestFormFields() + [widgets.TextField('a')])
    wlist = t.fields
    assert len(wlist) == 3, '%s' % [x.name for x in wlist]
    assert wlist[0].name == 'foo'
    assert wlist[1].name == 'bar'
    assert wlist[2].name == 'a'


def test_creation_overriding():

    class TestFormFields(widgets.WidgetsList):
        foo = widgets.TextField()
        bar = widgets.CheckBox()

    fields = TestFormFields()
    fields[1] = widgets.TextField('bar')
    t = widgets.TableForm(fields=fields)
    assert len(t.fields) == 2, '%s' % [x.name for x in t.fields]


def test_disabled_widget():
    form = widgets.TableForm(fields=[widgets.TextField('name'),
        widgets.TextField('age', validator=validators.Int())],
        submit_text='Submit')
    output = form.render(disabled_fields=['age'])
    assert 'age' not in output


def test_class_attributes_form():

    class TestForm(widgets.ListForm):
        fields =  [widgets.TextField('name'), widgets.TextField('age')]
        validator = validators.Schema()
        submit_text = 'gimme'

    form = TestForm()
    output = form.render()
    assert 'name' in output
    assert 'age' in output
    assert 'gimme' in output

    form = TestForm(fields = TestForm.fields + [widgets.TextField('phone')],
        submit_text = 'your number too')
    output = form.render()
    assert 'phone' in output
    assert 'your number too' in output


def test_help_text():
    class TestForm(widgets.ListForm):
        fields =  [
            widgets.TextField('name', help_text='Enter your name here'),
            widgets.TextField('age', help_text='Enter your age here')]
    form = TestForm()
    output = form.render()
    assert 'age here' in output
    assert 'name here' in output


def test_values_for_checkbox_list():
    w = widgets.CheckBoxList(options=list(enumerate(('apples', 'oranges'))))
    output = w.render()
    assert 'value="0"' in output and 'value="1"' in output
    assert 'value=""' not in output and 'value="None"' not in output
    assert "apples" in output and "oranges" in output


class CallableCounter:

    def __init__(self):
        self.counter = 0

    def __call__(self):
        self.counter += 1
        return [(1, 'foobar')]


def test_callable_options_for_selection_field():
    cc = CallableCounter()
    w = widgets.CheckBoxList('collections', label='Collections', options=cc)
    assert cc.counter == 1 # called once to guess validator
    cc = CallableCounter()
    w = widgets.CheckBoxList('collections', label='Collections', options=cc,
        validator=validators.Int())
    assert cc.counter == 0 # cc shouldn't be called if validator is provided


def test_default_value_adjustment():
    """Default values should be set before adjust_value is called."""
    class Widget1(widgets.Label):
        default = 'nolabel'
        use_super = True
        def adjust_value(self, value, **params):
            if self.use_super:
                value = super(Widget1, self).adjust_value(value, **params)
            if value:
                value += ' adjust1'
            return value
    class Widget2(Widget1):
        def adjust_value(self, value, **params):
            if self.use_super:
                value = super(Widget2, self).adjust_value(value, **params)
            if value:
                value += ' adjust2'
            return value
    w = Widget2()
    output = w.render('mylabel')
    assert '>mylabel adjust1 adjust2<' in output
    output = w.render()
    assert '>nolabel adjust1 adjust2<' in output
    Widget1.use_super = False
    output = w.render('mylabel')
    assert '>mylabel adjust2<' in output
    output = w.render()
    assert '>nolabel adjust2<' in output


nestedform = widgets.TableForm(fields=[
    widgets.FieldSet('foo', fields=[
        widgets.TextField('name'), widgets.TextField('age')])])


class NestedController(controllers.Controller):

    @expose()
    @validate(form=nestedform)
    def checkform(self, foo=None):
        return foo

    @expose()
    def field_for(self, engine='genshi'):
        request.validation_errors = dict(foo=dict(foo='error'))
        template = """<div xmlns:py="http://%s">
            <span py:replace="name"/> rendering with %s
            <span py:replace="field_for('foo').fq_name"/>.appears
            <span py:replace="field_for('foo').error"/>_appears
            <span py:replace="field_for('foo').field_id"/>_appears
            <span py:replace="field_for('foo')(value_for('foo'), **params_for('foo'))"/>
        </div>""" % (dict(genshi='genshi.edgewall.org/', kid='purl.org/kid/ns#'
            )[engine], engine)
        field = widgets.TextField('foo')
        fieldset = widgets.FieldSet('foo', fields=[field],
            template=template, engine_name=engine)
        form = widgets.Form('form', fields=[fieldset],
            template=template, engine_name=engine)
        # Good example below of how you can pass parameters and values
        # to nested widgets. Since the path acrobatics is a very delicate
        # issue, we make sure it works with both templating engines.
        value = dict(foo=dict(foo='HiYo!'))
        params = dict(attrs=dict(foo=dict(foo=dict(size=100))))
        params['format'] = 'xhtml'
        return form.render(value, **params)

    @expose()
    def repeating(self, abc=None):
        legend = abc and ["Range A", "Range B", "Range C"] or "Range"
        return widgets.RepeatingFieldSet(
            'my_fieldset', legend=legend, repetitions=5, fields=[
                widgets.TextField(name='lower', label="Lower"),
                widgets.TextField(name='upper', label="Upper")]).render()

def test_nested_variables():
    url = u'/checkform?foo.name=Kevin&foo.age=some%20Numero'.encode('utf-8')
    testutil.stop_server(tg_only = True)
    app = testutil.make_app(NestedController)
    testutil.start_server()
    request = app.get(url)
    assert config.app['/'].get('tools.decode.encoding') == 'utf-8'
    assert request.raw['name'] == 'Kevin'
    assert request.raw['age'] == u'some Numero'


def test_field_for():
    app = make_app(NestedController)
    for engine in 'genshi', 'kid':
        response = app.get('/field_for?engine=%s' % engine)
        assert '<div>' in response and '</div>' in response
        assert 'form rendering with %s' % engine in response
        assert 'foo rendering with %s' % engine in response
        assert 'form_foo_appears' in response
        assert 'form_foo_foo_appears' in response
        assert 'foo.appears' in response
        assert 'foo.foo.appears' in response
        assert 'error_appears' in response
        assert '<input ' in response
        assert 'type="text"' in response
        assert 'name="foo.foo"' in response
        assert 'id="form_foo_foo"' in response
        assert 'class="textfield erroneousfield"' in response
        assert 'value="HiYo!"' in response
        assert 'size="100"' in response


def test_value_repeater():
    """Test the ValueRepeater class"""
    vr = widgets.forms.ValueRepeater(None)
    assert bool(vr) is False
    vr = widgets.forms.ValueRepeater("foo")
    assert str(vr) == "foo"
    assert unicode(vr) == u"foo"
    assert vr[0] == "foo"
    assert vr[1] == "foo"
    assert vr[42] == "foo"
    assert bool(vr) is True
    vr = widgets.forms.ValueRepeater(["foo", "bar"])
    assert vr[0] == "foo"
    assert vr[1] == "bar"
    assert vr[2] == "foo"
    assert vr[42] == "foo"
    assert vr[43] == "bar"
    assert bool(vr) is True


def test_repeating_field_set():
    """Test the RepeatingFieldSet widget."""
    app = make_app(NestedController)
    output = app.get('/repeating').body
    assert 'id="my_fieldset_0"' in output
    assert 'name="my_fieldset-0.upper"' in output
    assert 'id="my_fieldset_4"' in output
    assert 'name="my_fieldset-4.upper"' in output
    assert 'id="my_fieldset_5"' not in output
    assert output.count('<legend>Range</legend>') == 5
    assert output.count('class="textfield"') == 10
    output = app.get('/repeating?abc=y').body
    assert 'id="my_fieldset_0"' in output
    assert '<legend>Range</legend>' not in output
    assert output.count('<legend>Range A</legend>') == 2
    assert output.count('<legend>Range B</legend>') == 2
    assert output.count('<legend>Range C</legend>') == 1
    assert output.count('class="textfield"') == 10

