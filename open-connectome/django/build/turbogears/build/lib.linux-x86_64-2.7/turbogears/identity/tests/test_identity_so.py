# -*- coding: UTF-8 -*-

"""SQLObject based Identity tests."""

import unittest
import urllib
import base64

from turbogears import testutil, database, config
from turbogears.identity.soprovider import TG_User, TG_Group, TG_Permission
from turbogears.identity.exceptions import IdentityConfigurationException
from turbogears.identity.visitor import IdentityVisitPlugin

from turbogears.identity.tests.test_identity import IdentityRoot

# hub = database.AutoConnectHub('sqlite:///:memory:')
hub = database.PackageHub('turbogears.identity')


class TestIdentity(testutil.TGTest):

    root = IdentityRoot

    stop_tg_only = True

    def setUp(self):
        test_config = {
            'visit.on': True,
            'visit.manager': 'sqlobject',
            'identity.on': True,
            'identity.provider': 'sqlobject',
            'identity.failure_url': '/identity_failed',
            'identity.force_external_redirect': False,
            'identity.source': 'form,http_auth,visit',
            'identity.http_basic_auth': True,
            'identity.http_auth_realm': 'test realm',
            'identity.form.user_name': 'user_name',
            'identity.form.password': 'password',
            'identity.form.submit': 'login',
            'identity.soprovider.encryption_algorithm': None,
            'identity.custom_encryption': None,
            'tg.strict_parameters': True,
            'tg.allow_json': False}
        if not self.config:
            original_config = dict()
            for key in test_config:
                original_config[key] = config.get(key)
            self.config = original_config
        config.configure_loggers(test_config)
        config.update(test_config)
        super(TestIdentity, self).setUp()
        config.update({'identity.http_basic_auth': False})
        self.init_model()


    def init_model(self):
        if TG_User.select().count() == 0:
            user = TG_User(user_name='samIam',
                email_address='samiam@example.com',
                display_name='Samuel Amicus', password='secret')
            admin_group = TG_Group(group_name='admin',
                display_name='Administrator')
            peon_group = TG_Group(group_name='peon',
                display_name='Regular Peon')
            other_group = TG_Group(group_name='other',
            display_name='Another Group')
            chopper_perm = TG_Permission(permission_name='chops_wood',
                description='Wood Chopper')
            boss_perm = TG_Permission(permission_name='bosses_people',
                description='Benevolent Dictator')
            peon_group.addTG_Permission(chopper_perm)
            admin_group.addTG_Permission(boss_perm)
            user.addTG_Group(peon_group)
            user.addTG_Group(other_group)
        self.root.current_in_peon_group = self.current_in_peon_group


    def current_in_peon_group(self, current):
        user = TG_User.by_user_name('samIam')
        group_ids = set((TG_Group.by_group_name('peon').id,
            TG_Group.by_group_name('other').id))
        assert current.user == user
        assert current.user_name == user.user_name
        assert current.user_id == user.id
        assert current.groups == set(('peon', 'other'))
        assert current.group_ids == group_ids


    def test_user_password_parameters(self):
        """Test that controller can receive user_name and password parameters."""
        response = self.app.get('/new_user_setup?user_name=test&password=pw')
        assert 'test pw' in response, response

    def test_user_exists(self):
        """Test that test user is present in data base."""
        user = TG_User.by_user_name('samIam')
        assert user.email_address == 'samiam@example.com'

    def test_user_password(self):
        """Test if we can set a user password (no encryption algorithm)."""
        hub.begin()
        user = TG_User.by_user_name('samIam')
        user.password = 'password'
        user.sync()
        assert user.password == 'password'
        hub.rollback()
        hub.end()

    def test_user_password_unicode(self):
        """Test if we can set a non-ascii user password (no encryption)."""
        config.update({'identity.soprovider.encryption_algorithm': None})
        self.app.get('/')
        hub.begin()
        user = TG_User.by_user_name('samIam')
        user.password = u'garçon'
        user.sync()
        assert user.password == u'garçon'
        hub.rollback()
        hub.end()

    def test_user_password_hashed_sha(self):
        """Test if a sha hashed password is stored in the database."""
        config.update({'identity.soprovider.encryption_algorithm': 'sha1'})
        self.app.get('/')
        hub.begin()
        user = TG_User.by_user_name('samIam')
        user.password = 'password'
        user.sync()
        assert user.password =='5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8'
        hub.rollback()
        hub.end()

    def test_user_password_hashed_sha_unicode(self):
        """Test if a non-ascii sha hashed password is stored in the database."""
        config.update({'identity.soprovider.encryption_algorithm': 'sha1'})
        self.app.get('/')
        hub.begin()
        user = TG_User.by_user_name('samIam')
        user.password = u'garçon'
        user.sync()
        assert user.password == '442edb21c491a6e6f502eb79e98614f3c7edf43e'
        hub.rollback()
        hub.end()

    def test_user_password_hashed_md5(self):
        """Test if a md5 hashed password is stored in the database."""
        config.update({'identity.soprovider.encryption_algorithm': 'md5'})
        self.app.get('/')
        hub.begin()
        user = TG_User.by_user_name('samIam')
        user.password = 'password'
        user.sync()
        assert user.password =='5f4dcc3b5aa765d61d8327deb882cf99'
        hub.rollback()
        hub.end()

    def test_user_password_hashed_md5_unicode(self):
        """Test if a non-ascii md5 hashed password is stored in the database."""
        config.update({'identity.soprovider.encryption_algorithm': 'md5'})
        self.app.get('/')
        hub.begin()
        user = TG_User.by_user_name('samIam')
        user.password = u'garçon'
        user.sync()
        assert user.password == 'c295c4bb2672ca8c432effc53b40bb1e'
        hub.rollback()
        hub.end()

    def test_user_password_hashed_md5_utf8string(self):
        """Test if a md5 hashed password with unicode characters is stored in
        the database if the password is entered as str (encoded in UTF-8). This
        test ensures that the encryption algorithm does handle non-unicode
        parameters gracefully."""
        config.update({'identity.soprovider.encryption_algorithm': 'md5'})
        self.app.get('/')
        hub.begin()
        user = TG_User.by_user_name('samIam')
        user.password = u'garçon'.encode('UTF-8')
        user.sync()
        assert user.password == 'c295c4bb2672ca8c432effc53b40bb1e'
        hub.rollback()
        hub.end()

    def test_user_password_raw(self):
        """Test that we can store raw values in the password field
        (without being hashed)."""
        config.update({'identity.soprovider.encryption_algorithm':'sha1'})
        self.app.get('/')
        hub.begin()
        user = TG_User.by_user_name('samIam')
        user.set_password_raw('password')
        user.sync()
        assert user.password =='password'
        hub.rollback()
        hub.end()

    def test_user_password_raw_unicode(self):
        """Test that unicode passwords are encrypted correctly"""
        config.update({'identity.soprovider.encryption_algorithm':'sha1'})
        self.app.get('/')
        hub.begin()
        user = TG_User.by_user_name('samIam')
        user.set_password_raw(u'garçon')
        user.sync()
        assert user.password == u'garçon'
        hub.rollback()
        hub.end()

    def test_user_password_hashed_custom(self):
        """Test if a custom hashed password is stored in the database."""
        config.update({'identity.soprovider.encryption_algorithm': 'custom',
            'identity.custom_encryption':
                'identity.tests.test_identity.mycustomencrypt'})
        self.app.get('/')
        hub.begin()
        user = TG_User.by_user_name('samIam')
        user.password = 'password'
        user.sync()
        assert user.password == 'password_custom'
        hub.rollback()
        hub.end()

    def test_anonymous_browsing(self):
        """Test if we can show up anonymously."""
        response = self.app.get('/is_anonymous')
        assert 'is_anonymous' in response, response

    def test_deny_anonymous(self):
        """Test that we have secured an url from anonymous users."""
        response = self.app.get('/logged_in_only', status=403)
        assert 'identity_failed_answer' in response, response

    def test_deny_anonymous_viewable(self):
        """Test that a logged in user can see an resource blocked
        from anonymous users."""
        response = self.app.get('/logged_in_only?'
            'user_name=samIam&password=secret&login=Login')
        assert 'logged_in_only' in response, response

    def test_external_redirect(self):
        """Test that external redirection at identity failures works."""
        config.update({'identity.failure_url': 'test_login',
            'identity.force_external_redirect': True})
        response = self.app.get('/logged_in_only?a=1&b=2', status=302)
        assert 'identity_failed_answer' not in response, response
        path, params = response.headers['Location'].split('?', 1)
        assert path.endswith('/test_login')
        params = '&'.join(sorted(params.split('&')))
        assert params == 'a=1&b=2&forward_url=%2Flogged_in_only'

    def test_external_redirect_with_funky_params(self):
        """Test that external redirection properly handles funky parameters."""
        config.update({'identity.force_external_redirect': True})
        response = self.app.get('/logged_in_only?'
            'a-0.x=1&a-0.y=2&a-1.x=3&a-1.y=4', status=302)
        assert 'identity_failed_answer' not in response, response
        path, params = response.headers['Location'].split('?', 1)
        assert path.endswith('/identity_failed')
        params = '&'.join(sorted(params.split('&')))
        assert params == ('a-0.x=1&a-0.y=2&a-1.x=3&a-1.y=4'
            '&forward_url=%2Flogged_in_only')

    def test_authenticate_header(self):
        """Test that identity returns correct WWW-Authenticate header."""
        response = self.app.get('/logged_in_only', status=403)
        assert 'WWW-Authenticate' not in response.headers
        config.update({'identity.http_basic_auth': True})
        response = self.app.get('/logged_in_only', status=401)
        assert response.headers['WWW-Authenticate'] == 'Basic realm="test realm"'

    def test_basic_authentication(self):
        """Test HTTP basic authentication mechanism."""
        config.update({'identity.http_basic_auth': True})
        credentials = base64.encodestring('samIam')[:-1]
        response = self.app.get('/logged_in_only', headers={
            'Authorization': 'Basic %s' % credentials}, status=401)
        assert 'identity_failed_answer' in response, response
        credentials = base64.encodestring('samIam:secret:appendix')[:-1]
        response = self.app.get('/logged_in_only', headers={
            'Authorization': 'Basic %s' % credentials}, status=401)
        assert 'identity_failed_answer' in response, response
        response = self.app.get('/logged_in_only', headers={
            'Authorization': 'Basic samIam:secret'}, status=401)
        assert 'identity_failed_answer' in response, response
        credentials = base64.encodestring('samIam:secret')[:-1]
        response = self.app.get('/logged_in_only', headers={
            'Authorization': 'Basic %s' % credentials})
        assert 'logged_in_only' in response, response

    def test_logout(self):
        """Test that logout works and session id gets invalid afterwards."""
        response = self.app.get('/in_peon_group?'
            'user_name=samIam&password=secret&login=Login')
        session_id = response.headers['Set-Cookie']
        response = self.app.get('/logout', headers={'Cookie': session_id})
        response = self.app.get('/is_anonymous', headers={'Cookie': session_id})
        assert response.body == 'is_anonymous'

    def test_require_group(self):
        """Test that a anonymous user can not access resource protected by
        require(in_group(...))"""
        response = self.app.get('/in_peon_group', status=403)
        assert 'identity_failed_answer' in response, response

    def test_require_expose_required_permission(self):
        """Test that the decorator exposes the correct permissions via _require
        attribute on the actual method."""
        response = self.app.get('/test_exposed_require')
        assert 'require is exposed' in response, response

    def test_user_and_group_properties(self):
        """Test that the current user and group properties are set correctly."""
        user = TG_User.by_user_name('samIam')
        assert user.user_name == 'samIam'
        group_ids = set((TG_Group.by_group_name('peon').id,
            TG_Group.by_group_name('other').id))
        assert group_ids == set((2, 3))

    def test_require_group_viewable(self):
        """Test that a user with proper group membership can see a restricted url."""
        response = self.app.get('/in_peon_group?'
            'user_name=samIam&password=secret&login=Login')
        assert 'in_peon_group' in response, response

    def test_user_not_in_right_group(self):
        """Test that only users in the right group have access."""
        response = self.app.get('/in_admin_group?'
            'user_name=samIam&password=secret&login=Login', status=403)
        assert 'identity_failed_answer' in response, response

    def test_require_permission(self):
        """Test that an anonymous user is denied access to a permission
        restricted url."""
        response = self.app.get('/has_chopper_permission', status=403)
        assert 'identity_failed_answer' in response, response

    def test_require_permission_viewable(self):
        """Test that a user with proper permissions can see a restricted url."""
        response = self.app.get('/has_chopper_permission?'
            'user_name=samIam&password=secret&login=Login')
        assert 'has_chopper_permission' in response, response

    def test_user_lacks_permission(self):
        """Test that a user is denied acces if they don't have the proper
        permission.
        """
        response = self.app.get('/has_boss_permission?'
            'user_name=samIam&password=secret&login=Login', status=403)
        assert 'identity_failed_answer' in response, response

    def test_user_info_available(self):
        """Test that we can see user information inside our controller."""
        response = self.app.get('/user_email?'
            'user_name=samIam&password=secret&login=Login')
        assert 'samiam@example.com' in response, response

    def test_bad_login(self):
        """Test that we are denied access if we provide a bad login."""
        response = self.app.get('/logged_in_only?'
            'user_name=samIam&password=wrong&login=Login', status=403)
        assert 'identity_failed_answer' in response, response

    def test_restricted_subdirectory(self):
        """Test that we can restrict access to a whole subdirectory."""
        response = self.app.get('/peon_area/index', status=403)
        assert 'identity_failed_answer' in response, response

    def test_restricted_subdirectory_viewable(self):
        """Test that we can access a restricted subdirectory
        if we have proper credentials."""
        response = self.app.get('/peon_area/index?'
            'user_name=samIam&password=secret&login=Login')
        assert 'restricted_index' in response, response

    def test_decoratator_in_restricted_subdirectory(self):
        """Test that we can require a different permission
        in a protected subdirectory."""
        response = self.app.get('/peon_area/in_other_group?'
            'user_name=samIam&password=secret&login=Login')
        assert 'in_other_group' in response, response

    def test_decoratator_failure_in_restricted_subdirectory(self):
        """Test that we can get an identity failure from a decorator
        in a restricted subdirectory"""
        response = self.app.get('/peon_area/in_admin_group?'
            'user_name=samIam&password=secret&login=Login', status=403)
        assert 'identity_failed_answer' in response, response

    def test_explicit_checks_in_restricted_subdirectory(self):
        """Test that explicit permission checks in a protected
        directory is handled as expected"""
        response = self.app.get('/peon_area/in_other_group_explicit_check?'
            'user_name=samIam&password=secret&login=Login')
        assert 'in_other_group' in response, response

    def test_throwing_identity_exception_in_restricted_subdirectory(self):
        """Test that throwing an IdentityException in a protected
        directory is handled as expected"""
        response = self.app.get('/peon_area/in_admin_group_explicit_check?'
            'user_name=samIam&password=secret&login=Login', status=403)
        assert 'identity_failed' in response, response

    def test_decode_filter_when_id_fails(self):
        """Test that the decode filter doesn't break with nested
        variables and Identity when credentials are bad"""
        params = urllib.quote(IdentityRoot._test_encoded_params, '=&')
        response = self.app.get('/test_params?' + params, status=403)
        assert 'identity_failed_answer' in response, response

    def test_decode_filter_when_id_works(self):
        """Test that the decode filter doesn't break with nested
        variables and Identity when credentials are good"""
        params = urllib.quote(IdentityRoot._test_encoded_params, '=&')
        params += '&user_name=samIam&password=secret&login=Login'
        response = self.app.get('/test_params?' + params)
        assert 'params ok' in response, response

    def test_user_unicode(self):
        """Test that we can have non-ascii user names."""
        user = TG_User(user_name=u'säm', display_name=u'Sämüel Käsfuß',
            email_address='samkas@example.com', password='geheim')
        assert user.user_name == u'säm'
        response = self.app.get('/logged_in_only?'
            'user_name=säm&password=geheim&login=Login')
        assert 'logged_in_only' in response, response
        self.app.reset()
        credentials = base64.encodestring('säm:geheim')[:-1]
        response = self.app.get('/logged_in_only', headers={
            'Authorization': 'Basic %s' % credentials})
        assert 'logged_in_only' in response, response

    def test_json(self):
        """Test that JSON controllers return the right status codes."""
        # We check that we get an authorization error, not the server error
        # caused by the identity_failure controller not accepting JSON.
        response = self.app.get('/json', status=403)
        # we get the output of the identity_failure controller in this case
        assert 'identity_failed_answer' in response, response
        response = self.app.get('/json?tg_format=json', status=403)
        # we get the right status code, but not the output of identity_failure
        assert 'identity_failed_answer' not in response, response
        assert 'Forbidden' in response, response
        response = self.app.get('/peon_area/json', status=403)
        assert 'identity_failed_answer' in response, response
        response = self.app.get('/peon_area/json?tg_format=json', status=403)
        assert 'identity_failed_answer' not in response, response
        response = self.app.get('/in_peon_group?'
            'user_name=samIam&password=secret&login=Login')
        assert 'in_peon_group' in response, response
        response = self.app.get('/json', status=200)
        assert 'restricted_json' in response, response
        response = self.app.get('/json?tg_format=json', status=200)
        assert 'restricted_json' in response, response
        response = self.app.get('/peon_area/json', status=200)
        assert 'restricted_json' in response, response
        response = self.app.get('/peon_area/json?tg_format=json', status=200)
        assert 'restricted_json' in response, response

    def test_remote_ip(self):
        """Test that our client IP is detected correctly."""
        r = self.app.get('/remote_ip', headers={'Remote-Addr': '127.0.0.1'},
            status=200)
        assert r.raw['remote_ip'] == '127.0.0.1'
        r = self.app.get('/remote_ip',
            headers={'X-Forwarded-For': '192.168.1.100, 224.50.214.12'},
            status=200)
        assert r.raw['remote_ip'] == '224.50.214.12'

    def test_from_localhost(self):
        """Test we can connect from 127.0.0.1."""
        r = self.app.get('/from_localhost', headers={'Remote-Addr': '192.168.4.100'},
            status=403)
        assert 'identity_failed_answer' in r
        r = self.app.get('/from_localhost', headers={'Remote-Addr': '127.0.0.1'},
            status=200)
        assert 'localhost_only' in r

    def test_from_any_host(self):
        """Test we can connect from any host in an IP list."""
        r = self.app.get('/from_any_host', headers={'Remote-Addr': '192.168.4.100'},
            status=403)
        assert 'identity_failed_answer' in r
        r = self.app.get('/from_any_host', headers={'Remote-Addr': '127.0.0.1'},
            status=200)
        assert 'hosts_on_list_only' in r
        r = self.app.get('/from_any_host', headers={'Remote-Addr': '127.0.0.2'},
            status=200)
        assert 'hosts_on_list_only' in r

    def test_nested_login(self):
        """Check that we can login using a nested form."""
        config.update({
            'identity.form.user_name': 'credentials.user',
            'identity.form.password': 'credentials.pass',
            'identity.form.submit': 'log.me.in'})
        testutil.stop_server(tg_only=False)
        self.app = testutil.make_app(self.root)
        testutil.start_server()
        response = self.app.get('/logged_in_only?'
            'credentials.user=samIam&credentials.pass=secret&log.me.in=Enter')
        assert 'logged_in_only' in response, response


class TestTGUser(testutil.DBTest):

    model = TG_User

    stop_tg_only = True

    def setUp(self):
        self._identity_on = config.get('identity.on', False)
        self._identity_provider = config.get('identity.provider', 'sqlalchemy')
        config.update({'identity.on': False,
            'identity.provider': 'sqlobject'})
        super(TestTGUser, self).setUp()

    def tearDown(self):
        testutil.stop_server()
        super(TestTGUser, self).tearDown()
        config.update({'identity.on': self._identity_on,
            'identity.provider': self._identity_provider})

    def test_create_user(self):
        """Test that User can be created outside of a running identity provider."""
        user = TG_User(user_name='testcase',
            email_address='testcase@example.com',
            display_name='Test Me', password='test')
        assert user.password == 'test', user.password


class TestIdentityVisitPlugin(unittest.TestCase):

    def setUp(self):
        test_config = {
            'visit.on': True,
            'visit.manager': 'sqlobject',
            'identity.on': True,
            'identity.http_basic_auth': True,
            'identity.provider': 'sqlobject',
            'identity.source': 'form, http_auth, visit, '}
        original_config = dict()
        for key in test_config:
            original_config[key] = config.get(key)
        self._original_config = original_config
        config.update(test_config)

    def tearDown(self):
        config.update(self._original_config)

    def test_identity_source(self):
        """Test that identity.source setting is parsed correctly."""
        plug = IdentityVisitPlugin()
        assert plug.identity_from_form in plug.identity_sources
        assert plug.identity_from_http_auth in plug.identity_sources
        assert plug.identity_from_visit in plug.identity_sources

    def test_no_identity_source(self):
        """Test that empty identity source raises identity configuration error."""
        config.update({'identity.source': ''})
        self.assertRaises(IdentityConfigurationException, IdentityVisitPlugin)

    def test_unknown_identity_source(self):
        """Test that unknown identity source raises identity configuration error."""
        config.update({'identity.source': 'bogus'})
        self.assertRaises(IdentityConfigurationException, IdentityVisitPlugin)

    def test_inactive_identity_source(self):
        """Test that inactive identity.source settings are removed."""
        config.update({'identity.source': 'http_auth,visit',
            'identity.http_basic_auth': False, 'visit.on': False})
        self.assertRaises(IdentityConfigurationException, IdentityVisitPlugin)

    def test_decode_credentials(self):
        """Test that HTTP basic auth credentials are decoded correctly."""
        plug = IdentityVisitPlugin()
        credentials = base64.encodestring('samIam:secret')[:-1]
        assert plug.decode_basic_credentials(credentials) == ['samIam', 'secret']
