import re

from turbogears import controllers, expose, testutil, validators, widgets
from turbogears.testutil import catch_validation_errors, start_server
from turbogears.widgets.meta import copy_schema


def setup_module():
    start_server()


int_validator = validators.Int(if_empty=None)
s_validator = validators.Schema(age=int_validator, ignore_key_missing=True)


class TestSchema(validators.Schema):
    """We ignore missing keys to make passing value easier in tests"""

    ignore_key_missing = True


class TestNestedWidgets:

    form = widgets.TableForm(name='myform', fields=[
        widgets.TextField('name'),
        widgets.TextField('age', validator=int_validator),
        widgets.FieldSet('sub', fields=[
            widgets.TextField('name'),
            widgets.TextField('age', validator=int_validator),
            widgets.FieldSet('sub2', fields=[
                widgets.TextField('name'),
                widgets.TextField('age', validator=int_validator)],
                validator=TestSchema())],
            validator=TestSchema())],
        validator=TestSchema())

    class MyRoot(controllers.RootController):

        @expose()
        def index(self, test_id):
            if test_id == 'age':
                data = dict(age=22)
            elif test_id == 'sub2':
                data = dict(sub=dict(sub2=dict(age=22)))
            elif test_id == 'sub':
                data = dict(dict(sub=dict(age=22)))
            return self.form.render(data)

    MyRoot.form = form

    def test_display(self):
        """Check that widget names are set correctly depending on their path."""
        app = testutil.make_app(self.MyRoot)
        response = app.get('/?test_id=sub2')
        output = response.body
        value_p = 'value="22"'
        name_p = 'name="sub.sub2.age"'
        assert (re.compile('.*'.join([value_p, name_p])).search(output)
            or re.compile('.*'.join([name_p, value_p])).search(output))
        response = app.get('/?test_id=sub')
        output = response.body
        value_p = 'value="22"'
        name_p = 'name="sub.age"'
        id_p = 'id="myform_sub_age"'
        assert (re.compile('.*'.join([value_p, name_p])).search(output)
            or re.compile('.*'.join([name_p, value_p])).search(output))
        assert (re.compile('.*'.join([value_p, id_p])).search(output)
            or re.compile('.*'.join([id_p, value_p])).search(output))
        response = app.get('/?test_id=age')
        output = response.body
        value_p = 'value="22"'
        name_p = 'name="age"'
        assert (re.compile('.*'.join([value_p, name_p])).search(output)
            or re.compile('.*'.join([name_p, value_p])).search(output))

    def test_validate_outermost(self):
        values = dict(age='twenty')
        values, errors = catch_validation_errors(self.form, values)
        assert errors.pop('age', False)
        assert not errors

    def test_validate_sub(self):
        values = dict(sub=dict(age='twenty'))
        values, errors = catch_validation_errors(self.form, values)
        # check the outermost dict is not polluted with errors
        # from the inner dicts
        assert 'age' not in errors
        errors = errors['sub']
        assert errors.pop('age', False)
        assert not errors

    def test_validate_sub2(self):
        values = dict(sub=dict(sub2=dict(age='twenty')))
        values, errors = catch_validation_errors(self.form, values)
        assert 'age' not in errors
        errors = errors['sub']
        assert 'age' not in errors
        errors = errors['sub2']
        assert errors.pop('age', False)
        assert not errors

    def test_validate_sub_and_sub2(self):
        values = dict(sub=dict(age='fhg', sub2=dict(age='twenty')))
        values, errors = catch_validation_errors(self.form, values)
        errors = errors['sub']
        assert errors.pop('age', False)
        errors = errors['sub2']
        assert errors.pop('age', False)
        assert not errors

    def test_good_values(self):
        values = dict(age=22, sub=dict(sub2=dict(age=20)))
        values, errors = catch_validation_errors(self.form, values)
        assert errors == {}
        assert values['age'] == 22

    def test_good_and_bad_values(self):
        values = dict(age='ddd', sub=dict(age='20', sub2=dict()))
        values, errors = catch_validation_errors(self.form, values)
        assert errors.pop('age', False)
        assert not errors
        # age is not converted
        assert values['sub']['age'] == '20'


class TestNestedWidgetsWSchemaValidation:

    form = widgets.TableForm(
        name='myform',
        validator=s_validator,
        fields=[
            widgets.TextField('name'),
            widgets.TextField('age'),
            widgets.FieldSet(
                name='sub',
                validator=s_validator,
                fields=[
                    widgets.TextField('name'),
                    widgets.TextField('age'),
                    widgets.FieldSet(
                        name = 'sub2',
                        validator=s_validator,
                        fields=[
                            widgets.TextField('name'),
                            widgets.TextField('age')])])])

    def test_validate_sub_schema(self):
        values = dict(sub=dict(age='twenty'))
        values, errors = catch_validation_errors(self.form, values)
        # check the outermost dict is not polluted
        # with errors from the inner dicts
        assert 'age' not in errors
        errors = errors['sub']
        assert errors.pop('age', False)
        assert not errors

    def test_good_and_bad_values_schema(self):
        values = dict(age='ddd', sub=dict(age='20', sub2=dict()))
        values, errors = catch_validation_errors(self.form, values)
        assert errors.pop('age', False)
        assert not errors
        # age is not converted
        assert values['sub']['age'] == '20'

    def test_good_values_schema(self):
        values = dict(age=22, sub=dict(sub2=dict(age=20)))
        values, errors = catch_validation_errors(self.form, values)
        assert errors == {}
        assert values['age'] == 22

    def test_validate_sub_and_sub2_schema(self):
        values = dict(sub=dict(age='fhg', sub2=dict(age='twenty')))
        values, errors = catch_validation_errors(self.form, values)
        assert 'age' not in errors
        errors = errors['sub']
        assert errors.pop('age', False)
        errors = errors['sub2']
        assert errors.pop('age', False)
        assert not errors

    def test_validate_sub2_schema(self):
        values = dict(sub=dict(sub2=dict(age='twenty')))
        values, errors = catch_validation_errors(self.form, values)
        assert 'age' not in errors
        errors = errors['sub']
        assert 'age' not in errors
        errors = errors['sub2']
        assert errors.pop('age', False)

    def test_validate_outermost_schema(self):
        values = dict(age='twenty')
        values, errors = catch_validation_errors(self.form, values)
        assert errors.pop('age', False)
        assert not errors
        assert not errors


class TestNestedWidgetsWMixedValidation:

    form = widgets.TableForm(
        name='myform',
        validator=s_validator,
        fields=[
            widgets.TextField('name'),
            widgets.TextField('age'),
            widgets.TextField('number', validator=int_validator),
            widgets.FieldSet(
                name='sub',
                validator=s_validator,
                fields=[
                    widgets.TextField('name'),
                    widgets.TextField('age'),
                    widgets.TextField('number', validator=int_validator),
                    widgets.FieldSet(
                        name='sub2',
                        fields=[
                            widgets.TextField('name'),
                            widgets.TextField('age',
                                validator=int_validator),
                            widgets.TextField('number',
                                validator=int_validator)])])])

    def test_mixed_validators(self):
        """Test that schema and single validators can be mixed safely."""
        values = dict(
            age='bad',
            number='22',
            sub=dict(
                age='bad',
                number='bad',
                sub2=dict(
                    age='bad',
                    number='bad')))
        values, errors = catch_validation_errors(self.form, values)
        assert errors.pop('age', False)
        # number is not converted
        assert values['number'] == '22'
        # assert errors are not getting polluted
        # with errors from other levels of the tree
        assert errors.keys() == ['sub']
        errors = errors['sub']
        assert errors.pop('age', False)
        assert errors.pop('number', False)
        assert errors.keys() == ['sub2']
        errors = errors['sub2']
        assert errors.pop('age', False)
        assert errors.pop('number', False)
        assert not errors



class InnerSchema(validators.Schema):

    ignore_key_missing = True
    age = int_validator


class MiddleSchema(validators.Schema):

    ignore_key_missing = True
    age = int_validator
    sub2 = InnerSchema()


class OuterSchema(validators.Schema):

    ignore_key_missing = True
    age = int_validator
    sub = MiddleSchema()


class TestNestedSchemaValidators:

    # Age is always validated by the nested schemas,
    # number is validated with widget validator.
    form = widgets.TableForm(
        name='myform',
        validator=OuterSchema(),
        fields=[
            widgets.TextField('age'),
            widgets.TextField('number', validator=int_validator),
            widgets.FieldSet(
                name='sub',
                fields=[
                    widgets.TextField('age'),
                    widgets.TextField('number', validator=int_validator),
                    widgets.FieldSet(
                        name = 'sub2',
                        fields = [
                            widgets.TextField('age'),
                            widgets.TextField('number',
                                validator=int_validator)])])])

    def test_nested_schemas(self):
        """Test that we can nest schema validators safely."""
        values = dict(
            age='bad',
            number='22',
            sub=dict(
                age='27',
                number='bad',
                sub2=dict(
                    age='bad',
                    number='bad')))
        values, errors = catch_validation_errors(self.form, values)
        assert errors.pop('age', False)
        # number is not converted
        assert values['number'] == '22'
        # assert errors are not getting polluted
        # with errors from other levels of the tree
        assert errors.keys() == ['sub']
        errors = errors['sub']
        values = values['sub']
        # age is not converted, but that's ok, since the schema
        # doesn't convert good values in invalid Schemas, ATM
        assert values['age'] == '27'
        assert errors.pop('number', False)
        assert errors.keys() == ['sub2']
        errors = errors['sub2']
        assert errors.pop('age', False)
        assert errors.pop('number', False)
        assert not errors

    def test_nested_schemas_good_values(self):
        values = dict(
            age='21',
            number='22',
            sub=dict(
                age='27',
                number='28',
                sub2=dict(
                    age='33',
                    number='34')))
        values, errors = catch_validation_errors(self.form, values)
        assert not errors
        assert (values['age'], values['number']) == (21, 22)
        values = values['sub']
        assert (values['age'], values['number']) == (27, 28)
        values = values['sub2']
        assert (values['age'], values['number']) == (33, 34)


def test_copy_schema():
    """Test that a validator schema can be copied."""

    class UserSchema(validators.Schema):
        user_name = validators.PlainText()

    schema = copy_schema(UserSchema())
    assert schema


def test_copy_nested_schema():
    """Test that a nested validator schema can be copied."""

    class PersonSchema(validators.Schema):

        class namefields(validators.Schema):
            firstname = validators.PlainText()
            lastname = validators.PlainText()

        class parents(validators.Schema):

            class father(validators.Schema):
                firstname = validators.PlainText()
                lastname = validators.PlainText()

            class mother(validators.Schema):
                firstname = validators.PlainText()
                lastname = validators.PlainText()

    schema = copy_schema(PersonSchema())
    assert schema
