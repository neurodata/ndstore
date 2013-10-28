
import unittest

import pkg_resources
import formencode
import cherrypy
try:
    import json
except ImportError: # Python < 2.6
    import simplejson as json

from turbogears import (absolute_url, config, controllers, database,
    error_handler, exception_handler, expose, flash, redirect,
    testutil, url, util, validate, validators)


def setup_module():
    testutil.start_server()

def teardown_module():
    testutil.stop_server()


rwt_called = 0
def rwt(func, *args, **kw):
    global rwt_called
    rwt_called += 1
    return func(*args, **kw)


class SubApp(controllers.RootController):

    @expose()
    def index(self):
        return url('/foo')


class MyRoot(controllers.RootController):

    value = None

    @expose()
    def index(self):
        return dict()

    def validation_error_handler(self, tg_source, tg_errors, *args, **kw):
        errors = {}
        for key, value in tg_errors.items():
            if hasattr(value, 'msg'):
                errors[key] = value.msg
            else:
                errors[key] = value
        return dict(msg="Error Message", values=kw, errors=errors,
                    functionname=tg_source.__name__)

    @expose('kid:turbogears.tests.simple', allow_json=True)
    def test(self):
        return dict(title='Foobar', mybool=False, someval='niggles')

    @expose()
    def invalid(self):
        return None

    @expose()
    def pos(self, posvalue):
        return dict(posvalue = posvalue)

    @expose()
    def servefile(self):
        return cherrypy.lib.static.serve_file(
            pkg_resources.resource_filename(
                'turbogears.tests', 'test_controllers.py'))

    @expose(content_type='text/plain')
    def basestring(self):
        return 'hello world'

    @expose(content_type='text/plain')
    def list(self):
        return ['hello', 'world']

    @expose(content_type='text/plain')
    def generator(self):
        yield 'hello'
        yield 'world'

    @expose()
    def unicode(self, response=None):
        if response is None:
            response = cherrypy.response
        response.headers['Content-Type'] = 'text/html'
        return u'\u00bfHabla espa\u00f1ol?'

    @expose()
    def returnedtemplate(self):
        return dict(title='Foobar', mybool=False, someval='foo',
            tg_template='kid:turbogears.tests.simple')

    @expose()
    def returnedtemplate_short(self):
        return dict(title='Foobar', mybool=False, someval='foo',
            tg_template='kid:turbogears.tests.simple')

    @expose('kid:turbogears.tests.simple')
    def exposetemplate_short(self):
        return dict(title='Foobar', mybool=False, someval='foo')

    @expose()
    @validate(validators={'value': validators.StringBoolean()})
    @error_handler(validation_error_handler)
    def istrue(self, value):
        self.value = value
        return str(value)

    @expose()
    @validate(validators={'value': validators.StringBoolean()})
    def nestedcall(self, value):
        return self.istrue(str(value))

    @expose()
    @validate(validators={'value': validators.ForEach(validators.Int())})
    def valuelist(self, value):
        return ','.join(map(str, value))

    @expose()
    @validate(validators={'value': validators.StringBoolean()})
    @error_handler(istrue)
    def errorchain(self, value):
        return {'error': 'No Error', 'value': self.value}

    @expose(format='json', template='kid:turbogears.tests.simple')
    def returnjson(self):
        return dict(title='Foobar', mybool=False, someval='foo',
            tg_template='kid:turbogears.tests.simple')

    @expose('kid:turbogears.tests.simple', allow_json=False)
    def allowjson(self):
        return dict(title='Foobar', mybool=False, someval='foo',
             tg_template='kid:turbogears.tests.simple')

    @expose(format='json')
    def impliedjson(self):
        return dict(title='Blah')

    @expose('json')
    def explicitjson(self):
        return dict(title='Blub')

    @expose('kid:turbogears.tests.simple', allow_json=True)
    def jsonerror_handler(self):
        return dict(someval='errors')

    @expose(allow_json=True)
    @exception_handler(jsonerror_handler)
    def jsonerror(self):
        raise ValueError

    @expose(content_type='xml/atom')
    def contenttype(self):
        return 'Foobar'

    @expose()
    @validate(validators={
        'firstname': validators.String(min=2, not_empty=True),
        'lastname': validators.String()})
    @error_handler(validation_error_handler)
    def save(self, submit, firstname, lastname='Miller'):
        fullname = '%s %s' % (firstname, lastname)
        return dict(firstname = firstname, lastname = lastname,
            fullname = fullname, submit = submit)


    class Registration(formencode.Schema):
        allow_extra_fields = True
        firstname = validators.String(min=2, not_empty=True)
        lastname = validators.String()

    @expose()
    @validate(validators=Registration())
    @error_handler(validation_error_handler)
    def save2(self, submit, firstname, lastname='Miller'):
        return self.save(submit, firstname, lastname)

    @expose('kid:turbogears.tests.simple')
    def useother(self):
        return dict(tg_template='kid:turbogears.tests.othertemplate')

    @expose('cheetah:turbogears.tests.simplecheetah')
    def usecheetah(self):
        return dict(someval='chimps')

    @expose('kid:turbogears.tests.simple', allow_json=True)
    def flash_plain(self):
        flash('plain')
        return dict(title='Foobar', mybool=False, someval='niggles')

    @expose('kid:turbogears.tests.simple', allow_json=True)
    def flash_unicode(self):
        flash(u'\xfcnicode')
        return dict(title='Foobar', mybool=False, someval='niggles')

    @expose('kid:turbogears.tests.simple', allow_json=True)
    def flash_data_structure(self):
        flash(dict(uni=u'\xfcnicode', testing=[1, 2, 3]))
        return dict(title='Foobar', mybool=False, someval='niggles')

    @expose('kid:turbogears.tests.simple', allow_json=True)
    def flash_redirect(self):
        flash(u'redirect \xfcnicode')
        redirect('/flash_redirected?tg_format=json')

    @expose('kid:turbogears.tests.simple', allow_json=True)
    def flash_redirected(self):
        return dict(title='Foobar', mybool=False, someval='niggles')

    @expose()
    def redirect(self):
        redirect('/foo')

    @expose()
    def raise_redirect(self):
        raise redirect('/foo')

    @expose()
    def relative_redirect(self):
        raise redirect('foo')

    @expose('kid:turbogears.tests.simple', allow_json=True)
    def flash_redirect_with_trouble_chars(self):
        flash(u'$foo, k\xe4se;\tbar!')
        redirect('/flash_redirected?tg_format=json')

    def exc_h_value(self, tg_exceptions=None):
        """Exception handler for the ValueError in raise_value_exc"""
        return dict(handling_value=True, exception=str(tg_exceptions))

    @expose()
    @exception_handler(exc_h_value, 'isinstance(tg_exceptions, ValueError)')
    def raise_value_exc(self):
        raise ValueError('Some Error in the controller')

    def exc_h_key(self, tg_exceptions=None):
        """Exception handler for KeyErrors in  raise_all_exc"""
        return dict(handling_key=True, exception=str(tg_exceptions))

    def exc_h_index(self, tg_exceptions=None):
        """Exception handler for the ValueError in raise_value_exc"""
        return dict(handling_index=True, exception=str(tg_exceptions))

    @expose()
    @exception_handler(exc_h_index, 'isinstance(tg_exceptions, IndexError)')
    def raise_index_exc(self):
        raise IndexError('Some IndexError')

    @expose()
    @exception_handler(exc_h_index, 'isinstance(tg_exceptions, IndexError)')
    @exception_handler(exc_h_value, 'isinstance(tg_exceptions, ValueError)')
    @exception_handler(exc_h_key, 'isinstance(tg_exceptions, KeyError)')
    def raise_all_exc(self, num=2):
        num = int(num)
        if num < 2:
            raise ValueError('Inferior to 2')
        elif num == 2:
            raise IndexError('Equals to 2')
        elif num > 2:
            raise KeyError('No such number 2 in the integer range')

    @expose()
    def internal_redirect(self, **kwargs):
        raise cherrypy.InternalRedirect('/internal_redirect_target')

    @expose()
    def internal_redirect_target(self, **kwargs):
        return 'redirected OK'

    @expose()
    def redirect_to_path_str(self, path):
        raise redirect(str(path) + '/index')

    @expose()
    def redirect_to_path_list(self, path):
        raise redirect([str(path), 'index'])

    @expose()
    def redirect_to_path_tuple(self, path):
        raise redirect((str(path), 'index'))

    @expose()
    def response_status_204_int(self):
        cherrypy.response.status = 204
        return

    @expose()
    def response_status_204_string(self):
        cherrypy.response.status = '204 No Content'
        return

    @expose()
    def absolute_url(self, url='/'):
        return absolute_url(url)


class TestRoot(testutil.TGTest):

    stop_tg_only = True

    def setUp(self):
        testutil.mount(MyRoot(), '/')
        testutil.mount(SubApp(), '/subthing')
        self.app = testutil.make_app()
        super(TestRoot, self).setUp()


    def test_js_files(self):
        """Can access the JavaScript files"""
        response = self.app.get('/tg_js/MochiKit.js', status=200)
        assert response.headers['Content-Type'] in (
            'text/javascript', 'text/x-js',
            'application/javascript', 'application/x-javascript')

    def test_json_output(self):
        response = self.app.get('/test?tg_format=json')
        values = json.loads(response.body)
        assert values == dict(title='Foobar', mybool=False,
            someval='niggles', tg_flash=None)
        assert response.headers['Content-Type'] == 'application/json'

    def test_implied_json(self):
        response = self.app.get('/impliedjson?tg_format=json')
        assert '"title": "Blah"' in response
        assert response.headers['Content-Type'] == 'application/json'

    def test_explicit_json(self):
        response = self.app.get('/explicitjson')
        assert '"title": "Blub"' in response
        assert response.headers['Content-Type'] == 'application/json'
        response = self.app.get('/explicitjson?tg_format=json')
        assert '"title": "Blub"' in response
        assert response.headers['Content-Type'] == 'application/json'

    def test_allow_json(self):
        response = self.app.get('/allowjson?tg_format=json', status=404)
        assert response.headers['Content-Type'] in ('text/html',
            'text/html;charset=utf-8')

    def test_allow_json_config(self):
        """JSON output can be enabled via config."""
        config.update({'tg.allow_json':True})
        class JSONRoot(controllers.RootController):
            @expose('kid:turbogears.tests.simple')
            def allowjsonconfig(self):
                return dict(title='Foobar', mybool=False, someval='foo',
                     tg_template='kid:turbogears.tests.simple')
        app = testutil.make_app(JSONRoot)
        response = app.get('/allowjsonconfig?tg_format=json')
        assert response.headers['Content-Type'] == 'application/json'
        config.update({'tg.allow_json': False})

    def test_allow_json_config_false(self):
        """Make sure JSON can still be restricted with a global config on."""
        config.update({'tg.allow_json': False})
        class JSONRoot(controllers.RootController):
            @expose('kid:turbogears.tests.simple')
            def allowjsonconfig(self):
                return dict(title='Foobar', mybool=False, someval='foo',
                     tg_template='kid:turbogears.tests.simple')
        testutil.stop_server()
        app = testutil.make_app(JSONRoot)
        testutil.start_server()
        response = app.get('/allowjsonconfig')
        assert response.headers['Content-Type'] in ('text/html',
            'text/html; charset=utf-8')
        response = app.get('/allowjsonconfig?tg_format=json', status=404)
        assert response.headers['Content-Type'] in ('text/html',
            'text/html;charset=utf-8')
        config.update({'tg.allow_json': True})

    def test_json_error(self):
        """The error handler should return JSON if requested."""
        response = self.app.get('/jsonerror')
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'
        assert 'Paging all errors' in response.body
        response = self.app.get('/jsonerror?tg_format=json')
        assert response.headers['Content-Type'] == 'application/json'
        assert '"someval": "errors"' in response.body

    def test_invalid_return(self):
        response = self.app.get('/invalid', status=500)
        assert response.headers['Content-Type'] in ('text/html',
            'text/html;charset=utf-8')

    def test_strict_parameters(self):
        config.update({'tg.strict_parameters': True})
        response = self.app.get(
            '/save?submit=save&firstname=Foo&lastname=Bar&badparam=1',
            status=500)
        assert 'unexpected keyword argument' in response

    def test_throw_out_random(self):
        """Can append random value to the URL to avoid caching problems."""
        response = self.app.get('/test?tg_random=1')
        assert 'Paging all niggles' in response
        config.update({'tg.strict_parameters': True})
        response = self.app.get('/test?tg_random=1', status=200)
        assert 'Paging all niggles' in response
        response = self.app.get('/test?tg_not_random=1', status=500)
        assert 'unexpected keyword argument' in response

    def test_ignore_parameters(self):
        config.update({'tg.strict_parameters': True})
        response = self.app.get('/test?ignore_me=1', status=500)
        assert 'unexpected keyword argument' in response
        config.update({'tg.ignore_parameters': ['ignore_me', 'me_too']})
        response = self.app.get('/test?ignore_me=1')
        assert 'Paging all niggles' in response
        response = self.app.get('/test?me_too=1', status=200)
        assert 'Paging all niggles' in response
        response = self.app.get('/test?me_not=1', status=500)
        assert 'unexpected keyword argument' in response

    def test_retrieve_dict_directly(self):
        response = self.app.get('/returnjson')
        assert response.raw['title'] == 'Foobar'

    def test_template_output(self):
        response = self.app.get('/test')
        assert 'Paging all niggles' in response

    def test_unicode(self):
        response = self.app.get('/unicode')
        firstline = response.body.split('\n', 1)[0].decode('utf-8')
        assert firstline == u'\u00bfHabla espa\u00f1ol?'

    def test_default_format(self):
        """The default format can be set via expose"""
        response = self.app.get('/returnjson')
        assert '"title": "Foobar"' in response
        response = self.app.get('/returnjson?tg_format=html', status=404)

    def test_content_type(self):
        """The content-type can be set via expose"""
        response = self.app.get('/contenttype')
        assert response.headers['Content-Type'] == 'xml/atom'

    def test_returned_template_name(self):
        response = self.app.get('/returnedtemplate')
        data = response.body.lower()
        assert '<body>' in data
        assert 'groovy test template' in data

    def test_returned_template_short(self):
        response = self.app.get('/returnedtemplate_short')
        assert 'Paging all foo' in response

    def test_expose_template_short(self):
        response = self.app.get('/exposetemplate_short')
        assert 'Paging all foo' in response

    def test_validation(self):
        """Data can be converted and validated"""
        response = self.app.get('/istrue?value=true')
        assert response.body == 'True'
        response = self.app.get('/istrue?value=false')
        assert response.body == 'False'

        app = testutil.make_app(MyRoot)
        response = app.get('/istrue?value=foo')
        assert response.raw['msg'] == 'Error Message'

        response = app.get('/save?submit=send&firstname=John&lastname=Doe')
        assert response.raw['fullname'] == 'John Doe'
        assert response.raw['submit'] == 'send'
        response = app.get('/save?submit=send&firstname=Arthur')
        assert response.raw['fullname'] == 'Arthur Miller'
        response = app.get('/save?submit=send&firstname=Arthur&lastname=')
        assert response.raw['fullname'] == 'Arthur '
        response = app.get('/save?submit=send&firstname=D&lastname=')
        assert len(response.raw['errors'].keys()) == 1
        assert 'firstname' in response.raw['errors']
        assert 'characters' in response.raw['errors']['firstname'].lower()
        response = app.get('/save?submit=send&firstname=&lastname=')
        assert len(response.raw['errors'].keys()) == 1
        assert 'firstname' in response.raw['errors']

    def test_validation_chained(self):
        """Validation is not repeated if it already happened"""
        response = self.app.get('/errorchain?value=true')
        assert response.raw['value'] is None
        self.app.get('/errorchain?value=notbool')
        assert 'No Error' in response.body
        assert response.raw['value'] is None

    def test_validation_nested(self):
        """Validation is not repeated in nested method call"""
        response = self.app.get('/nestedcall?value=true')
        assert response.body == 'True', response.body
        response = self.app.get('/nestedcall?value=false')
        assert response.body == 'False', response.body

    def test_validation_list_get(self):
        """Multiple values can be passed as list with the get method."""
        response = self.app.get('/valuelist?value=')
        assert response.body == ''
        response = self.app.get('/valuelist?value=42')
        assert response.body == '42'
        response = self.app.get('/valuelist?value=4&value=2')
        assert response.body == '4,2', "values not properly passed as list"

    def test_validation_list_post(self):
        """Multiple values can be passed as list with the post method."""
        response = self.app.post('/valuelist',
            'value=',
            {'Content-Type': 'application/x-www-form-urlencoded'})
        assert response.body == ''
        response = self.app.post('/valuelist',
            'value=42',
            {'Content-Type': 'application/x-www-form-urlencoded'})
        assert response.body == '42'
        response = self.app.post('/valuelist',
            'value=4&value=2',
            {'Content-Type': 'application/x-www-form-urlencoded'})
        assert response.body == '4,2', "values not properly passed as list"
        response = self.app.post('/valuelist',
            '--AaB03x\r\nContent-Disposition: form-data;'
            ' name="value"\r\n\r\n\r\n--AaB03x--',
            {'Content-Type': 'multipart/form-data; boundary=AaB03x'})
        assert response.body == ''
        response = self.app.post('/valuelist',
            '--AaB03x\r\nContent-Disposition: form-data;'
            ' name="value"\r\n\r\n42\r\n--AaB03x--',
            {'Content-Type': 'multipart/form-data; boundary=AaB03x'})
        assert response.body == '42'
        response = self.app.post('/valuelist',
            '--AaB03x\r\nContent-Disposition: form-data;'
            ' name="value"\r\n\r\n4\r\n'
            '--AaB03x\r\nContent-Disposition: form-data;'
            ' name="value"\r\n\r\n2\r\n--AaB03x--',
            {'Content-Type': 'multipart/form-data; boundary=AaB03x'})
        # fails with CherryPy 3.2.0rc1 because of CherryPy bug #1028
        assert response.body == '4,2', "values not properly passed as list"

    def test_validation_with_schema(self):
        """Data can be converted/validated with formencode.Schema instance"""
        response = self.app.get('/save2?submit=send&firstname=Joe&lastname=Doe')
        assert response.raw['fullname'] == 'Joe Doe'
        assert response.raw['submit'] == 'send'
        response = self.app.get('/save2?submit=send&firstname=Arthur&lastname=')
        assert response.raw['fullname'] == 'Arthur '
        response = self.app.get('/save2?submit=send&firstname=&lastname=')
        assert len(response.raw['errors']) == 1
        assert 'firstname' in response.raw['errors']
        response = self.app.get('/save2?submit=send&firstname=D&lastname=')
        assert len(response.raw['errors']) == 1
        assert 'firstname' in response.raw['errors']

    def test_other_template(self):
        """tg_template in a returned dict will use the template specified there"""
        response = self.app.get('/useother')
        assert 'This is the other template' in response

    def test_cheetah_template(self):
        """Cheetah templates can be used as well"""
        response = self.app.get('/usecheetah')
        assert 'This is the Cheetah test template.' in response
        assert 'Paging all chimps.' in response

    def test_run_with_trans(self):
        """run_with_transaction is called only on topmost exposed method"""
        oldrwt = database.run_with_transaction
        database.run_with_transaction = rwt
        response = self.app.get('/nestedcall?value=true')
        database.run_with_transaction = oldrwt
        assert response.body == 'True'
        assert rwt_called == 1

    def test_positional(self):
        """Positional parameters should work"""
        response = self.app.get('/pos/foo')
        assert response.raw['posvalue'] == 'foo'

    def test_flash_plain(self):
        """flash with strings should work"""
        response = self.app.get('/flash_plain?tg_format=json')
        values = json.loads(response.body)
        assert values['tg_flash'] == 'plain'
        assert 'tg_flash' not in response.headers

    def test_flash_unicode(self):
        """flash with unicode objects should work"""
        response = self.app.get('/flash_unicode?tg_format=json')
        values = json.loads(response.body)
        assert values['tg_flash'] == u'\xfcnicode'
        assert 'tg_flash' not in response.headers

    def test_flash_on_redirect(self):
        """flash must survive a redirect"""
        response = self.app.get('/flash_redirect?tg_format=json', status=302)
        response = self.app.get(response.location,
            headers=dict(Cookie=response.headers['Set-Cookie']))
        values = json.loads(response.body)
        assert values['tg_flash'] == u'redirect \xfcnicode'

    def test_flash_redirect_with_trouble_chars(self):
        """flash redirect with chars that can cause troubles in cookies"""
        response = self.app.get('/flash_redirect_with_trouble_chars?tg_format=json', status=302)
        response = self.app.get(response.location,
            headers=dict(Cookie=response.headers['Set-Cookie']))
        values = json.loads(response.body)
        assert values['tg_flash'] == u'$foo, k\xe4se;\tbar!'

    def test_double_flash(self):
        """latest set flash should have precedence"""
        # Here we are calling method that sets a flash message. However flash
        # cookie is still there. Turbogears should discard old flash message
        # from cookie and use new one, set by flash_plain().
        response = self.app.get('/flash_plain?tg_format=json',
            headers=dict(Cookie='tg_flash="old flash"; Path=/;'))
        values = json.loads(response.body)
        assert values['tg_flash'] == 'plain'
        assert 'tg_flash' in response.cookies_set, \
            'Cookie clearing request should be present'

    def test_set_kid_outputformat_in_config(self):
        """the outputformat for kid can be set in the config"""
        config.update({'kid.outputformat': 'xhtml'})
        response = self.app.get('/test')
        assert '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML ' in response
        config.update({'kid.outputformat': 'html'})
        response = self.app.get('/test')
        assert  '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML ' in response
        assert '    This is the groovy test ' in response
        config.update({'kid.outputformat': 'html compact'})
        response = self.app.get('/test')
        assert  '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML ' in response
        assert 'This is the groovy test ' in response
        assert '    ' not in response

    def test_fileserving(self):
        response = self.app.get('/servefile')
        assert 'def test_fileserving' in response

    def test_basestring(self):
        response = self.app.get('/basestring')
        assert 'hello world' in response
        assert response.headers['Content-Type'] == 'text/plain'

    def test_list(self):
        response = self.app.get('/list')
        assert 'helloworld' in response
        assert response.headers['Content-Type'] == 'text/plain'

    def test_generator(self):
        response = self.app.get('/generator')
        assert 'helloworld' in response
        assert response.headers['Content-Type'] == 'text/plain'

    def test_internal_redirect(self):
        """regression test for #1022, #1407 and #1598"""
        response = self.app.get('/internal_redirect')
        assert 'redirected OK' in response

    def test_internal_redirect_nested_variables(self):
        """regression test for #1022, #1407 and #1598"""
        response = self.app.get(
            '/internal_redirect?a=1&a-1.b=2&a-2.c=3&a-2.c-1=4')
        assert 'redirected OK' in response

    def test_exc_value(self):
        """Exception is handled gracefully by the right exception handler."""
        response = self.app.get('/raise_value_exc')
        assert 'handling_value' in response

    def test_exc_index(self):
        """Exception is handled gracefully by the right exception handler."""
        response = self.app.get('/raise_index_exc')
        assert 'handling_index' in response

    def test_exc_all(self):
        """Test a controller that is protected by multiple exception handlers.

        It should raise either of the 3 exceptions but all should be handled
        by their respective handlers without problem...

        """
        response = self.app.get('/raise_all_exc?num=1')
        assert 'handling_value' in response
        response = self.app.get('/raise_all_exc?num=2')
        assert 'handling_index' in response
        response = self.app.get('/raise_all_exc?num=3')
        assert 'handling_key' in response

    def test_no_content_response(self):
        """HTTP response status 204 (No Content) is handled correctly.

        204 responses should have bo body and no content type set.

        """
        response = self.app.get('/response_status_204_string', status=204)
        assert 'Content-type' not in response.headers
        assert not response.body
        response = self.app.get('/response_status_204_int', status=204)
        assert 'Content-type' not in response.headers
        assert not response.body


class TestURLs(testutil.TGTest):
    stop_tg_only = True

    def setUp(self):
        testutil.mount(MyRoot(), '/')
        testutil.mount(SubApp(), '/subthing')
        testutil.mount(SubApp(), '/subthing/subsubthing')
        self.app = testutil.make_app()
        super(TestURLs, self).setUp()

    def tearDown(self):
        super(TestURLs, self).tearDown()
        config.update({'server.webpath': ''})


    def test_basic_urls(self):
        self.app.get('/')
        assert url('foo') == 'foo'
        assert url('/foo') == '/foo'
        assert url(['foo', 'bar']) == 'foo/bar'
        assert url('/foo', bar=1, baz=2) in [
            '/foo?bar=1&baz=2', '/foo?baz=2&bar=1']
        assert url('/foo', dict(bar=1, baz=2)) in [
            '/foo?bar=1&baz=2', '/foo?baz=2&bar=1']
        assert url('/foo', dict(bar=1, baz=None)) == '/foo?bar=1'
        assert url('http://foo.bar') == 'http://foo.bar'
        assert url('https://foo.bar') == 'https://foo.bar'

    def test_url_without_request_available(self):
        # Stopping the server in tearDown ensures that there's no request
        assert not util.request_available()
        assert url('foo') == 'foo'
        assert url('/foo') == '/foo'
        assert url('http://foo.bar') == 'http://foo.bar'

    def test_url_with_path(self):
        config.update({'server.webpath': '/coolsite/root'})
        assert url('foo') == 'foo'
        assert url('/foo') == '/coolsite/root/foo'
        assert url('http://foo.bar') == 'http://foo.bar'

    def test_approots(self):
        response = self.app.get('/subthing/', status=200)
        assert '/subthing/foo' in response
        response = self.app.get('/nosubthing/', status=404)
        assert '/subthing/foo' not in response

    def test_lower_approots(self):
        response = self.app.get('/subthing/subsubthing/')
        assert '/subthing/subsubthing/foo' in response

    def test_approots_with_path(self):
        config.update({'server.webpath': '/coolsite/root'})
        response = self.app.get('/subthing/')
        assert '/coolsite/root/subthing/foo' in response

    def test_redirect(self):
        config.update({'server.webpath': '/coolsite/root'})
        response = self.app.get('/redirect')
        assert response.location == 'http://localhost:80/coolsite/root/foo'
        self.app.get('/raise_redirect')
        assert response.location == 'http://localhost:80/coolsite/root/foo'
        self.app.get('/relative_redirect')
        assert response.location == 'http://localhost:80/coolsite/root/foo'

    def test_redirect_to_path(self):
        for path_type in ('str', 'list', 'tuple'):
            for path in ('subthing', '/subthing'):
                url = '/redirect_to_path_%s?path=%s' % (path_type, path)
                response = self.app.get(url, status=302)
                location = response.location
                assert location == 'http://localhost:80/subthing/index'

    def test_multi_values(self):
        self.app.get('/')
        assert url('/foo', bar=[1, 2]) in [
            '/foo?bar=1&bar=2', '/foo?bar=2&bar=1']
        assert url('/foo', bar=('asdf', 'qwer')) in [
            '/foo?bar=qwer&bar=asdf', '/foo?bar=asdf&bar=qwer']

    def test_unicode(self):
        """url() can handle unicode parameters"""
        self.app.get('/')
        assert url('/', x=u'\N{LATIN SMALL LETTER A WITH GRAVE}'
            u'\N{LATIN SMALL LETTER E WITH GRAVE}'
            u'\N{LATIN SMALL LETTER I WITH GRAVE}'
            u'\N{LATIN SMALL LETTER O WITH GRAVE}'
            u'\N{LATIN SMALL LETTER U WITH GRAVE}') \
            == '/?x=%C3%A0%C3%A8%C3%AC%C3%B2%C3%B9'

    def test_list(self):
        """url() can handle list parameters, with unicode too"""
        self.app.get('/')
        assert url('/', foo=['bar', u'\N{LATIN SMALL LETTER A WITH GRAVE}']
            ) == '/?foo=bar&foo=%C3%A0'

    def test_existing_query_string(self):
        """url() can handle URL with existing query string"""
        self.app.get('/')
        test_url = url('/foo', {'first': 1})
        assert url(test_url, {'second': 2}) == '/foo?first=1&second=2'

    def test_index_trailing_slash(self):
        """If there is no trailing slash on an index method call, redirect"""
        testutil.mount(SubApp(), '/')
        testutil.mount(SubApp(), '/foo')
        # CherryPy 3.1 gives 302, CherryPy 3.2 gives 301
        self.app.get('/foo', status=(301, 302))

    def test_can_use_internally_defined_arguments(self):
        """Can use argument names that are internally used by TG in controllers"""

        class App(controllers.RootController):

            @expose()
            def index(self, **kw):
                return '\n'.join(['%s:%s' % i for i in kw.iteritems()])

        testutil.mount(App(), '/')
        response = self.app.get('/?format=foo&template=bar&fragment=boo')
        assert 'format:foo' in response
        assert 'template:bar' in response
        assert 'fragment:boo' in response

    def test_url_kwargs_overwrite_tgparams(self):
        """Keys in tgparams in call to url() overwrite kw args"""
        params = {'spamm': 'eggs'}
        assert 'spamm=ham' in url('/foo', params, spamm='ham')

    def test_url_doesnt_change_tgparams(self):
        """url() does not change the dict passed as second arg"""
        params = {'spamm': 'eggs'}
        assert 'foo' in url('/foo', params, spamm='ham')
        assert params['spamm'] == 'eggs'


class TestAbsoluteURLs(testutil.TGTest):
    root = MyRoot
    stop_tg_only = True

    def _config_update(self, data=None, **kw):
        self.config_backup = {}
        if not data:
            data = {}
        else:
            data = data.copy()
        data.update(kw)
        for k in data:
            val = config.get(k)
            if k == 'server.socket_host' and not val:
                # When socket_host is set, CP3 checks to make sure it's valid,
                # even though it's default value is blank. So, if it's blank,
                # reset it to a bogus value.
                hostname = 'bar.net'
            else:
                self.config_backup[k] = config.get(k)
        config.update(data)

    def _config_reset(self):
        config.update(self.config_backup)

    def test_scheme_from_config(self):
        """absolute_url() gets correct URL scheme from tg.url_scheme setting"""
        hostname = 'foo.org'
        scheme = 'https'
        self._config_update({
            'base_url_filter.on': False,
            'base_url_filter.use_x_forwarded_host': True,
            'tg.url_scheme': scheme
        })
        url = self.app.get('/absolute_url/?url=%2Ffoo',
            headers={'X-Forwarded-Host': hostname}).body
        self._config_reset()
        assert url == '%s://%s/foo' % (scheme, hostname)

    def test_scheme_from_header(self):
        """absolute_url() gets correct URL scheme from 'X-Use-SSL' header"""
        hostname = 'foo.org'
        scheme = 'https'
        self._config_update({
            'base_url_filter.on': False,
            'base_url_filter.use_x_forwarded_host': True,
        })
        url = self.app.get('/absolute_url/?url=%2Ffoo',
            headers={'X-Forwarded-Host': hostname, 'X-Use-SSL': scheme}).body
        self._config_reset()
        assert url == '%s://%s/foo' % (scheme, hostname)

    def test_use_base_url(self):
        """absolute_url() gets correct host name from 'base_url' setting"""
        hostname = 'foo.org'
        port = 1234
        self._config_update({
            'base_url_filter.on': True,
            'base_url_filter.use_x_forwarded_host': False,
            'base_url_filter.base_url': 'http://%s:%s' % (hostname, port)
        })
        url = self.app.get('/absolute_url/?url=%2Ffoo').body
        self._config_reset()
        print url
        assert url == 'http://%s:%s/foo' % (hostname, port)

    def test_use_config(self):
        """absolute_url() gets correct host name from 'tg.url_domain' setting"""
        hostname = 'foo.org'
        port = 1234
        self._config_update({
            'base_url_filter.on': False,
            'base_url_filter.use_x_forwarded_host': False,
            'tg.url_domain': '%s:%s' % (hostname, port)
        })
        url = self.app.get('/absolute_url/?url=%2Ffoo').body
        self._config_reset()
        print url
        assert url == 'http://%s:%s/foo' % (hostname, port)

    def test_use_host(self):
        """absolute_url() gets correct host name from 'Host' header"""
        self._config_update({
            'base_url_filter.on': False,
            'base_url_filter.use_x_forwarded_host': False,
        })
        hostname = 'foo.org'
        url = self.app.get('/absolute_url/?url=%2Ffoo',
            headers={'Host': hostname}).body
        self._config_reset()
        print url
        assert url == 'http://%s/foo' % hostname

    def test_use_server_config(self):
        """absolute_url() gets correct host name from server config"""
        hostname = 'foo.org'
        port = 1234
        self._config_update({
            'base_url_filter.on': False,
            'base_url_filter.use_x_forwarded_host': False,
            'server.socket_host': hostname,
            'server.socket_port': port
        })
        url = self.app.get('/absolute_url/?url=%2Ffoo',
            headers={'Host': ''}).body
        self._config_reset()
        print url
        assert url == 'http://%s:%s/foo' % (hostname, port)

    def test_use_x_forwarded_host(self):
        """absolute_url() gets correct host name from 'X-Forwarded-Host' header"""
        self._config_update({
            'base_url_filter.on': False,
            'base_url_filter.use_x_forwarded_host': True,
        })
        hostname = 'foo.org'
        url = self.app.get('/absolute_url/?url=%2Ffoo',
            headers={'X-Forwarded-Host': hostname}).body
        self._config_reset()
        print url
        assert url == 'http://%s/foo' % hostname
