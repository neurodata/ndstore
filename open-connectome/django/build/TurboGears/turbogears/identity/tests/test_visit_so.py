# -*- coding: UTF-8 -*-

"""SQLObject based Visit tests."""

import time

from Cookie import SimpleCookie
from unittest import TestCase

import turbogears.visit.api
from turbogears import config, testutil, visit
from turbogears.visit.sovisit import SqlObjectVisitManager

from turbogears.identity.tests.test_visit import (
    SimpleVisitPlugin, VisitRoot, cookie_header)


class TestVisit(TestCase):

    def setUp(self):
        testutil.stop_server(tg_only=True)
        self._visit_on = config.get('visit.on', False)
        self._visit_manager = config.get('visit.manager', 'sqlalchemy')
        self._visit_timeout = config.get('visit.timeout', 20)
        self._visit_source = config.get('visit.source', 'cookie')
        self._visit_key_param = config.get('visit.form.name', 'tg_visit')
        self.cookie_name = config.get('visit.cookie.name', 'tg-visit')
        config.update({'visit.on': True,
            'visit.manager': 'sqlobject',
            'visit.timeout': 50})
        self.app = testutil.make_app(VisitRoot)
        testutil.start_server(tg_only=True)

    def tearDown(self):
        testutil.stop_server(tg_only=True)
        config.update({'visit.timeout': self._visit_timeout,
            'visit.on': self._visit_on,
            'visit.manager': self._visit_manager})

    def test_visit_response(self):
        """Test if the visit cookie is set in cherrypy.response."""
        response = self.app.get('/')
        assert self.cookie_name in response.cookies_set

    def test_new_visit(self):
        """Test that we can see a new visit on the server."""
        response = self.app.get('/')
        assert response.raw['new']

    def test_old_visit(self):
        """Test if we can track a visitor over time."""
        response = self.app.get('/')
        # first visit's cookie
        response.cookies_set[self.cookie_name]
        response = self.app.get('/', headers=cookie_header(response))
        assert not response.raw['new']

    def test_visit_from_form(self):
        """Test if the visit key is retrieved from the request params."""
        _app = self.app
        try:
            testutil.stop_server(tg_only=True)
            config.update({'visit.source': 'cookie,form'})
            self.app = testutil.make_app(VisitRoot)
            testutil.start_server()
            # first visit's cookie
            first_key = self.app.get('/').raw.get('key')
            # second request with no cookies
            self.app.cookies = {}
            response = self.app.get('/',
                params={self._visit_key_param: first_key})
        finally:
            config.update({'visit.source': self._visit_source})
            self.app = _app
        assert first_key == response.raw['key']

    def test_visit_from_form_with_cookie_fallback(self):
        """Test if visit key is retrieved from cookie if not found in params."""
        _app = self.app
        try:
            testutil.stop_server(tg_only=True)
            config.update({'visit.source': 'form,cookie'})
            _app = testutil.make_app(VisitRoot)
            testutil.start_server()
            # first visit's cookie
            first_key = self.app.get('/').raw.get('key')
            # second request with no params
            response = self.app.get('/')
        finally:
            config.update({'visit.source': self._visit_source})
            self.app = _app
        assert first_key == response.raw['key']

    def test_cookie_expires(self):
        """Test if the visit timeout mechanism works."""
        timeout = config.get('visit.timeout', 50)
        _app = self.app
        try:
            # set expiration to one second for this test only
            testutil.stop_server(tg_only=True)
            config.update({'visit.timeout': 1.0/60})
            self.app = testutil.make_app(VisitRoot)
            testutil.start_server()
            response = self.app.get('/')
            morsel = response.cookies_set[self.cookie_name]
            time.sleep(2) # 2 seconds
            response = self.app.get('/', headers=cookie_header(response))
        finally:
            config.update({'visit.timeout': timeout})
            self.app = _app
        assert response.cookies_set[
                self.cookie_name] != morsel, \
            'cookie values should not match'
        assert response.raw['new'], \
            'this should be a new visit, as the cookie has expired'

    def test_cookie_not_permanent(self):
        """Check that by default the visit cookie is not permanent."""
        response = self.app.get('/')
        cookies = SimpleCookie(response.headers['Set-Cookie'])
        morsel = cookies[self.cookie_name]
        assert not morsel['expires'] and not morsel['max-age']

    def test_cookie_permanent(self):
        """Check that the visit cookie can be made permanent."""
        permanent = config.get('visit.cookie.permanent', False)
        try:
            # set cookie permanent for this test only (needs restart)
            testutil.stop_server(tg_only=False)
            config.update({'visit.cookie.permanent': True})
            app = testutil.make_app(VisitRoot)
            testutil.start_server()
            response = app.get('/')
            cookies = SimpleCookie(response.headers['Set-Cookie'])
            morsel = cookies[self.cookie_name]
        finally:
            config.update({'visit.cookie.permanent': permanent})
        assert morsel['max-age'] == '3000'
        expires = time.mktime(time.strptime(morsel['expires'],
            '%a, %d-%b-%Y %H:%M:%S GMT')[:8] + (0,))
        should_expire = time.mktime(time.gmtime()) + int(morsel['max-age'])
        assert abs(should_expire - expires) < 3, (should_expire, expires, should_expire - expires)

    def test_visit_plugin(self):
        """Visit plugins are registered correctly and called for each request."""
        plug = SimpleVisitPlugin()
        plug.register()
        response1 = self.app.get('/visit_plugin')
        key = response1.raw['key']
        response2 = self.app.get('/visit_plugin')
        assert key == response2.raw['key']
        assert not response2.raw['is_new']


class MyVisitManager(SqlObjectVisitManager):
    pass


class TestSetVisitManager(TestCase):

    def setUp(self):
        testutil.stop_server(tg_only=True)
        self._visit_on = config.get('visit.on', False)
        self._visit_manager = config.get('visit.manager', 'sqlalchemy')
        self._visit_timeout = config.get('visit.timeout', 20)
        config.update({'visit.on': True,
            'visit.manager': 'sqlobject',
            'visit.timeout': 50})

    def tearDown(self):
        testutil.stop_server(tg_only=True)
        config.update({'visit.on': self._visit_on,
            'visit.manager': self._visit_manager,
            'visit.timeout': self._visit_timeout})

    def test_visit_manager_from_class(self):
        """Visit manager class is loaded correctly from dotted-path notation."""
        config.update({'visit.manager':
            'turbogears.identity.tests.test_visit_so.MyVisitManager'})
        testutil.start_server()
        assert isinstance(turbogears.visit.api._manager, MyVisitManager)

    def test_visit_manager_from_plugin(self):
        """Visit manager class is loaded correctly from entry point plugin."""
        config.update({'visit.manager': 'sqlobject'})
        testutil.start_server()
        assert isinstance(turbogears.visit.api._manager, SqlObjectVisitManager)

    def test_visit_manager_faiL_missing(self):
        """Runtime Exception is raised when no visit manager class is found."""
        config.update({'visit.manager': 'bogus'})
        self.assertRaises(RuntimeError, visit.start_extension)
