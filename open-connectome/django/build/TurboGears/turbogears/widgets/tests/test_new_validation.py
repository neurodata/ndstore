
from turbogears import validators, widgets
from turbogears.testutil import catch_validation_errors


class SimpleSchema(validators.Schema):

    phone = validators.Int()


class NotSoSimpleSchema(SimpleSchema):

    def to_python(self, value, state=None):
        value = super(NotSoSimpleSchema, self).to_python(value, state)
        age = value.pop('age')
        phone = value.pop('phone')
        value['phoneage'] = age + phone
        return value


class SimpleFields(widgets.WidgetsList):

    age = widgets.TextField(validator=validators.Int())
    phone = widgets.TextField()


class SimpleForm(widgets.Form):

    fields = SimpleFields()
    validator = SimpleSchema()


class SimpleFieldSet(widgets.FieldSet):
    
    name = 'fs'
    fields = SimpleFields()
    validator = SimpleSchema()


class TestSimpleForm:

    def test_simple_form(self):
        """We can validate a simple form """
        form = SimpleForm()
        value = dict(age='22', phone='5555555')
        value = form.validate(value)
        assert value == dict(age=22, phone=5555555)

    def test_simple_form_bad(self):
        """We can validate a simple form with errors """
        form = SimpleForm()
        value = dict(age="bad", phone="5555555")
        value, errors = catch_validation_errors(form, value)
        assert errors.pop('age')
        assert not errors

    def test_simple_form_bad2(self):
        """We can validate a simple form with errors, error from the schema """
        form = SimpleForm()
        value = dict(age='22', phone='bad')
        value, errors = catch_validation_errors(form, value)
        assert errors.pop('phone')
        assert not errors

    def test_not_so_simple_schema(self):
        """We can validate a form with a custom schema"""
        form = SimpleForm(validator=NotSoSimpleSchema())
        value = dict(age='22', phone='5555555')
        value = form.validate(value)
        assert value == dict(phoneage=5555577)


class TestNestedForm:

    def test_nested_form(self):
        """We can validate a form with a nested fieldset."""
        form = SimpleForm(fields=SimpleForm.fields + [SimpleFieldSet()])
        value = dict(age='22', phone='5555555',
            fs=dict(age='22', phone='5555555'))
        value = form.validate(value)
        assert value == dict(age=22, phone=5555555,
            fs=dict(age=22, phone=5555555))

    def test_nested_form_bad(self):
        """We can validate a form with a nested fieldset with errors."""
        form = SimpleForm(fields=SimpleForm.fields + [SimpleFieldSet()])
        value = dict(age='22', phone='5555555',
            fs=dict(age='bad', phone='5555555'))
        value, errors = catch_validation_errors(form, value)
        assert errors['fs'].pop('age')
        assert not errors.pop('fs')
        assert not errors

    def test_nested_form_bad2(self):
        """We can validate a form with nested fieldset with errors."""
        form = SimpleForm(fields=SimpleForm.fields + [SimpleFieldSet()])
        value = dict(age='22', phone='5555555',
            fs=dict(age='22', phone='bad'))
        value, errors = catch_validation_errors(form, value)
        assert errors['fs'].pop('phone')
        assert not errors.pop('fs')
        assert not errors
