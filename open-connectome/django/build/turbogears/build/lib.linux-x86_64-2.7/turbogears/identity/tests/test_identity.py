# -*- coding: UTF-8 -*-

"""ORM independent Identity tests and test controllers."""

import unittest

import formencode
import cherrypy

from turbogears import identity, expose
from turbogears.controllers import Controller, RootController
from turbogears.identity import (SecureObject, SecureResource,
    in_group, in_all_groups, in_any_group, not_anonymous,
    has_permission, has_all_permissions, has_any_permission,
    from_host, from_any_host, Any, All, NotAny)
from turbogears.identity.conditions import _remoteHost
from turbogears.identity.exceptions import RequestRequiredException


def mycustomencrypt(password):
    """A custom password encryption function."""
    return password + '_custom'


class MockIdentity(object):
    """Identity mock object."""

    anonymous = False
    groups = ('admin', 'edit')
    permissions = ('read', 'write')

mock_identity = MockIdentity()


class TestPredicates(unittest.TestCase):

    def met(self, predicate):
        return predicate.eval_with_object(mock_identity)

    def test_in_group(self):
        """Test the predicate for requiring a group."""
        assert self.met(in_group('admin'))
        assert not self.met(in_group('guest'))

    def test_in_all_groups(self):
        """Test the predicate for requiring a number of group."""
        assert self.met(in_all_groups('admin', 'edit'))
        assert not self.met(in_all_groups('admin', 'guest', 'edit'))

    def test_in_any_group(self):
        """Test the predicate for requiring at least one group."""
        assert self.met(in_any_group('guest', 'edit', 'user'))
        assert not self.met(in_all_groups('guest', 'user'))

    def test_anonymous(self):
        """Test predicate for checking anonymous visitors."""
        assert self.met(not_anonymous())

    def test_has_permission(self):
        """Test predicate for checking particular permissions."""
        assert self.met(has_permission('read'))
        assert not self.met(has_permission('delete'))

    def test_has_all_permissions(self):
        """Test the predicate for requiring a number of permissions."""
        assert self.met(has_all_permissions('read', 'write'))
        assert not self.met(has_all_permissions('read', 'delete', 'write'))

    def test_has_any_permission(self):
        """Test the predicate for requiring at least one permission."""
        assert self.met(has_any_permission('delete', 'write', 'update'))
        assert not self.met(has_any_permission('delete', 'update'))

    def test_any(self):
        """Test the Any predicate."""
        yes = in_group('edit')
        no1, no2 = in_group('guest'), in_group('user')
        met = self.met
        assert met(Any(yes))
        assert not met(Any(no1, no2))
        assert met(Any(no1, yes, no2))

    def test_all(self):
        """Test the All predicate."""
        yes1, yes2 = in_group('admin'), in_group('edit')
        no = in_group('guest')
        met = self.met
        assert not met(All(no))
        assert met(All(yes1, yes2))
        assert not met(All(yes1, no, yes2))

    def test_not_any(self):
        """Test the Not Any predicate."""
        yes = in_group('edit')
        no1, no2 = in_group('guest'), in_group('user')
        met = self.met
        assert not met(NotAny(yes))
        assert met(NotAny(no1, no2))
        assert not met(NotAny(no1, yes, no2))

    def test_remote_host_request_required(self):
        """Test that _remoteHost raises exception when request is not available.
        """
        self.assertRaises(RequestRequiredException, _remoteHost)


class TestSecureObject(unittest.TestCase):

    def test_secure_object_proxies_cp_attributes(self):
        """Test that SecureObject properly proxies CherryPy (_cp) attributes."""

        test_config = {'request.methods_with_bodies': ('POST', 'PUT')}

        class TestObject(object):
            _cp_config = test_config

        test_object = SecureObject(TestObject(), None)
        assert test_object._cp_config == test_config

        test_object = SecureObject(RootController(), None)
        test_object._cp_config = test_config
        assert test_object._cp_config == test_config

    def test_secure_object_proxies_setattr(self):
        """Test that SecureObject also proxies attributes assigned later."""

        class TestObject(object):
            pass

        test_object = SecureObject(TestObject(), None)
        assert isinstance(test_object._object, TestObject)

        test_object.value = 'value'
        assert test_object._object.value == 'value'


class RestrictedArea(Controller, SecureResource):

    require = in_group('peon')

    @expose()
    def index(self):
        return "restricted_index"

    @expose()
    @identity.require(in_group('admin'))
    def in_admin_group(self):
        return 'in_admin_group'

    @expose()
    @identity.require(in_group('other'))
    def in_other_group(self):
        return 'in_other_group'

    @expose()
    def in_admin_group_explicit_check(self):
        if 'admin' not in identity.current.groups:
            raise identity.IdentityFailure("You need to be an Admin")
        else:
            return 'in_admin_group'

    @expose()
    def in_other_group_explicit_check(self):
        if 'other' not in identity.current.groups:
            raise identity.IdentityException
        else:
            return 'in_other_group'

    @expose(format='json')
    def json(self):
        return dict(json="restricted_json")


class IdentityRoot(RootController):

    @expose()
    def index(self):
        return dict()

    @expose(format='html')
    def identity_failed(self, **kw):
        """Identity failure - this usually returns a login form."""
        return 'identity_failed_answer'

    @expose()
    @identity.require(not_anonymous())
    def logged_in_only(self):
        return 'logged_in_only'

    @expose()
    @identity.require(in_group('peon'))
    def in_peon_group(self):
        current = identity.current
        self.current_in_peon_group(current)
        request = cherrypy.serving.request
        assert current.user_name == request.identity.user_name
        return 'in_peon_group'

    @expose()
    def remote_ip(self):
        return dict(remote_ip=_remoteHost())

    @expose()
    @identity.require(from_host('127.0.0.1'))
    def from_localhost(self):
        return 'localhost_only'

    @expose()
    @identity.require(from_any_host(('127.0.0.1', '127.0.0.2')))
    def from_any_host(self):
        return 'hosts_on_list_only'

    @expose()
    def test_exposed_require(self):
        if not hasattr(self.in_peon_group, '_require'):
            return 'no _require attr'
        if not isinstance(self.in_peon_group._require, in_group):
            return 'not correct class'
        if 'peon' != self.in_peon_group._require.group_name:
            return 'not correct group name'
        return '_require is exposed'

    @expose()
    @identity.require(in_group('admin'))
    def in_admin_group(self):
        return 'in_admin_group'

    @expose()
    @identity.require(has_permission('chops_wood'))
    def has_chopper_permission(self):
        return 'has_chopper_permission'

    @expose()
    @identity.require(has_permission('bosses_people'))
    def has_boss_permission(self):
        return 'has_boss_permission'

    @expose()
    def logout(self):
        identity.current.logout()
        return 'logged out'

    @expose()
    @identity.require(not_anonymous())
    def user_email(self):
        return identity.current.user.email_address

    peon_area = RestrictedArea()

    @expose()
    def new_user_setup(self, user_name, password):
        return '%s %s' % (user_name, password)

    _test_encoded_params = 'b=krümel&d.a=klöße1'

    @expose()
    @identity.require(not_anonymous())
    def test_params(self, **kwargs):
        params = self._test_encoded_params
        # formencode's variable_decode create a datastructure
        #  but does not "decode" anything
        to_datastruct = formencode.variabledecode.variable_decode
        expected_params = to_datastruct(
            dict([p.split('=') for p in params.split('&')]))
        params_ok = True
        if not expected_params['b'].decode(
                'utf-8') == cherrypy.request.params['b']:
            params_ok = False
        if not expected_params['d']['a'].decode(
                'utf-8') == cherrypy.request.params['d']['a']:
            params_ok = False
        if params_ok:
            return 'params ok'
        else:
            return ("wrong params: %s\n"
                "expected unicode objects for all strings"
                % cherrypy.request.params)

    @expose()
    def is_anonymous(self):
        assert cherrypy.serving.request.identity.user_name is None
        assert cherrypy.serving.request.identity.anonymous
        assert identity.current.anonymous
        return 'is_anonymous'

    @expose(format='json')
    @identity.require(in_group('peon'))
    def json(self):
        return dict(json='restricted_json')
