"""Tests for paginate"""

from urllib import quote

import cherrypy

from sqlalchemy import Table, Column, ForeignKey, Integer, String
from sqlalchemy.orm import mapper, relation
from sqlobject import SQLObject, IntCol, StringCol

from turbojson.jsonify import jsonify

from turbogears import config, expose, database, testutil
from turbogears.controllers import RootController
from turbogears.database import bind_metadata, metadata, session
from turbogears.paginate import paginate, sort_ordering, sort_data
from turbogears.testutil import sqlalchemy_cleanup

query_methods = 'Q QA SO SL'.split()

__connection__ = hub = database.PackageHub('test_paginate')


class listlike(object):
    """A minimum list-like object that is needed for paginate."""

    def __init__(self, *args):
        self._list = list(*args)

    def __len__(self):
        return len(self._list)

    def __getitem__(self, key):
        return self._list[key]


def test_sort_ordering():
    """Test the sort_ordering auxiliary function."""
    s = []
    sort_ordering(s, 'a')
    assert s == ['a']
    sort_ordering(s, 'a') # descending order
    assert s == ['-a']
    sort_ordering(s, 'b')
    assert s == ['b', '-a']
    sort_ordering(s, 'c')
    assert s == ['c', 'b', '-a']
    sort_ordering(s, 'c') # descending order
    assert s == ['-c', 'b', '-a']
    sort_ordering(s, 'a') # 'a' again... still in descending order
    assert s == ['-a', '-c', 'b']
    sort_ordering(s, 'a') # 'a' again... now in ascending order
    assert s == ['a', '-c', 'b']
    sort_ordering(s, 'd')
    assert s == ['d', 'a', '-c', 'b']
    sort_ordering(s, 'a')
    assert s == ['a', 'd', '-c', 'b']


def test_sort_in_memory():
    """Test sorting in memory only."""
    for access in range(2):
        if access:
            # ordinary attribute access with hashable keys
            class row(object):
                def __init__(self, ab):
                    self.ab = ab
                    self.a, self.b = self.ab = ab
                def __repr__(self):
                    return self.ab
                def __cmp__(self, other):
                    return cmp(self.ab, other.ab)
        else:
            # dictionary access with unhashable keys
            class row(dict):
                def __init__(self, ab):
                    self.ab = ab
                    self['a'], self['b'] = map(list, ab)
                def __repr__(self):
                    return self.ab
                def __cmp__(self, other):
                    return cmp(self.ab, other.ab)
        def make_data(rows):
            return map(row, rows.split())
        ab = make_data('aa ab ba bb')
        aB = make_data('ab aa bb ba')
        Ab = make_data('ba bb aa ab')
        AB = make_data('bb ba ab aa')
        ba = make_data('aa ba ab bb')
        bA = make_data('ba aa bb ab')
        Ba = make_data('ab bb aa ba')
        BA = make_data('bb ab ba aa')
        if access:
            assert (not isinstance(ab[0], dict)
                and getattr(ab[0], 'a', 'b') == 'a')
        else:
            assert (isinstance(ab[0], dict) and ab[0].get('a', 'b') == ['a']
                and getattr(ab[0], 'a', 'b') == 'b')
        assert sort_data(ab, []) == ab
        assert sort_data(ab, ['b'], False) == ab
        assert sort_data(ab, ['a']) == ab
        assert sort_data(ab, ['a', 'b']) == ab
        assert sort_data(ab, ['a', '-b']) == aB
        assert sort_data(ab, ['b']) == ba
        assert sort_data(ab, ['b', 'a']) == ba
        assert sort_data(ab, ['b', '-a']) == bA
        assert sort_data(ab, ['-a']) == Ab
        assert sort_data(ab, ['-a', 'b']) == Ab
        assert sort_data(ab, ['-a', '-b']) == AB
        assert sort_data(ab, ['-b']) == Ba
        assert sort_data(ab, ['-b', 'a']) == Ba
        assert sort_data(ab, ['-b', '-a']) == BA
        assert sort_data(aB, ['a', 'b']) == ab
        assert sort_data(Ab, ['a', 'b']) == ab
        assert sort_data(AB, ['a', 'b']) == ab
        assert sort_data(ba, ['a', 'b']) == ab
        assert sort_data(bA, ['a', 'b']) == ab
        assert sort_data(Ba, ['a', 'b']) == ab
        assert sort_data(BA, ['a', 'b']) == ab
        assert sort_data(aB, ['b', 'a']) == ba
        assert sort_data(Ab, ['b', 'a']) == ba
        assert sort_data(AB, ['b', 'a']) == ba
        assert sort_data(ba, ['b', 'a']) == ba
        assert sort_data(bA, ['b', 'a']) == ba
        assert sort_data(Ba, ['b', 'a']) == ba
        assert sort_data(BA, ['b', 'a']) == ba
        assert sort_data(aB, ['-a', 'b']) == Ab
        assert sort_data(Ab, ['-a', 'b']) == Ab
        assert sort_data(AB, ['-a', 'b']) == Ab
        assert sort_data(ba, ['-a', 'b']) == Ab
        assert sort_data(bA, ['-a', 'b']) == Ab
        assert sort_data(Ba, ['-a', 'b']) == Ab
        assert sort_data(BA, ['-a', 'b']) == Ab
        assert sort_data(aB, ['b', '-a']) == bA
        assert sort_data(Ab, ['b', '-a']) == bA
        assert sort_data(AB, ['b', '-a']) == bA
        assert sort_data(ba, ['b', '-a']) == bA
        assert sort_data(bA, ['b', '-a']) == bA
        assert sort_data(Ba, ['b', '-a']) == bA
        assert sort_data(BA, ['b', '-a']) == bA


class Spy(object):
    """Helper class to test paginate's instances in cherrypy.request.

    We could use a special template to output paginate's attributes, but
    testing values/types before they are rendered (when possible) is much
    easier.
    """

    def __init__(self, name=None, **expectations):
        self.name = name
        self.expectations = expectations

    def __str__(self):
        if self.name:
            paginate = cherrypy.request.paginates[self.name]
        else:
            paginate = cherrypy.request.paginate
            assert paginate in cherrypy.request.paginates.values()
        for k, v in self.expectations.iteritems():
            if not hasattr(paginate, k):
                return "fail: paginate does not have '%s' attribute" % k
            w = getattr(paginate, k)
            if isinstance(v, xrange):
                v = list(v)
            if isinstance(w, xrange):
                w = list(w)
            if w != v:
                return "fail: expected %s=%r, got %s=%r" % (k, v, k, w)
        return "ok: [paginate %s ]" % ', '.join(
            ['%s=%r' % (k, v) for k, v in paginate.__dict__.items()])

    @staticmethod
    def assert_ok(body, key, value, raw=False):
        assert "ok: [paginate" in body
        if raw:
            expr = '%s=%s' % (key, value)
        else:
            expr = '%s=%r' % (key, value)
        # some simplejson versions escape forward slashes, so fix this
        body = body.replace('\\/', '/')
        assert expr in body, "expected %s" % expr

@jsonify.when('isinstance(obj, Spy)')
def jsonify_spy(obj):
    result = str(obj)
    return result


class TestPagination(testutil.TGTest):
    """Base class for all Paginate TestCases"""

    def setUp(self):
        self.root = self.MyRoot
        super(TestPagination, self).setUp()

    def request(self, url, status=200):
        response = self.app.get(url, status=status)
        self.body = response.body
        if "fail: " in self.body:
            assert False, ("Spy alert! Check output:\n%s" % self.body)


class TestSpy(TestPagination):
    """Never trust a spy"""

    class MyRoot(RootController):

        @expose()
        @paginate('data')
        def spy(self):
            data = range(100)
            spy = Spy()
            return dict(data=data, spy=spy)

        @expose()
        @paginate('data')
        def spy_correct_expectation(self):
            data = range(100)
            spy = Spy(page_count=10)
            return dict(data=data, spy=spy)

        @expose()
        @paginate('data')
        def spy_wrong_expectation(self):
            data = range(100)
            spy = Spy(page_count=9)
            return dict(data=data, spy=spy)

        @expose()
        @paginate('data')
        def spy_invalid_expectation(self):
            data = range(100)
            spy = Spy(foobar=10)
            return dict(data=data, spy=spy)

    def test_spy(self):
        response = self.app.get('/spy')
        Spy.assert_ok(response.body, 'current_page', 1)
        try:
            Spy.assert_ok(response.body, 'current_page', 2)
            raise Exception("above test should have failed")
        except AssertionError:
            pass

    def test_correct_expectation(self):
        response = self.app.get('/spy_correct_expectation')
        assert "ok: [paginate" in response

    def test_wrong_expectation(self):
        response = self.app.get('/spy_wrong_expectation')
        assert "fail: expected page_count=9, got page_count=10" in response

    def test_invalid_expectation(self):
        response = self.app.get('/spy_invalid_expectation')
        assert "fail: paginate does not have 'foobar' attribute" in response

    def test_raw_expectation(self):
        response = self.app.get('/spy_correct_expectation')
        Spy.assert_ok(response.body, 'var_name', 'data')
        Spy.assert_ok(response.body, 'var_name', "'data'", raw=True)


class TestBasicPagination(TestPagination):

    class MyRoot(RootController):

        @expose()
        @paginate('data', limit=4)
        def basic(self):
            spy = Spy(var_name='data', pages=xrange(1, 4), limit=4,
                      page_count=3, order=None, ordering=[], row_count=10)
            data = range(10)
            return dict(data=data, spy=spy)

        @expose()
        @paginate('data', limit=4)
        def listlike(self):
            spy = Spy(var_name='data', pages=xrange(1, 4), limit=4,
                      page_count=3, order=None, ordering=[], row_count=10)
            data = listlike(range(10))
            return dict(data=data, spy=spy)

        @expose()
        @paginate('data', limit=4, max_limit=None)
        def custom_limit(self):
            spy = Spy(var_name='data', order=None, ordering=[], row_count=10)
            data = range(10)
            return dict(data=data, spy=spy)

        @expose()
        @paginate('data', limit=4, max_limit=7)
        def max_limit(self):
            spy = Spy(var_name='data', order=None, ordering=[], row_count=10)
            data = range(10)
            return dict(data=data, spy=spy)

        @expose()
        @paginate('data')
        def default_max_pages(self):
            spy = Spy(var_name='data', limit=10, page_count=10,
                      order=None, ordering=[], row_count=100)
            data = range(100)
            return dict(data=data, spy=spy)

        @expose()
        @paginate('data', max_pages=4)
        def four_max_pages(self):
            spy = Spy(var_name='data', limit=10, page_count=10,
                      order=None, ordering=[], row_count=100)
            data = range(100)
            return dict(data=data, spy=spy)

        @expose()
        @paginate('data', max_pages=3)
        def three_max_pages(self):
            spy = Spy(var_name='data', limit=10, page_count=10,
                      order=None, ordering=[], row_count=100)
            data = range(100)
            return dict(data=data, spy=spy)

        @expose()
        @paginate('data', limit=4, dynamic_limit='foobar')
        def invalid_dynamic(self):
            data = range(10)
            return dict(data=data)

        @expose()
        @paginate('data', limit=4, dynamic_limit='foobar', max_limit=None)
        def dynamic(self):
            spy = Spy(var_name='data', pages=xrange(1, 3), limit=7,
                      page_count=2, order=None, ordering=[], row_count=10)
            data = range(10)
            return dict(data=data, spy=spy, foobar=7)

        @expose()
        @paginate('bar')
        @paginate('foo', limit=4)
        def multiple(self):
            spy_foo = Spy(name='foo', var_name='foo',
                          pages=xrange(1, 6), limit=4, page_count=5,
                          order=None, ordering=[], row_count=20)
            spy_bar = Spy(name='bar', var_name='bar',
                          pages=xrange(1, 4), limit=10, page_count=3,
                          order=None, ordering=[], row_count=26)
            foo = range(20)
            bar = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') # 26 letters
            return dict(foo=foo, bar=bar, spy_foo=spy_foo, spy_bar=spy_bar)

        @expose()
        @paginate('data', limit=4, max_limit=None)
        def empty(self):
            spy = Spy(var_name='data', pages=xrange(1, 1), page_count=0,
                      order=None, ordering=[], row_count=0,
                      current_page=1, first_item=0, last_item=0)
            data = []
            return dict(data=data, spy=spy)


    def test_pagination(self):
        self.request('/basic?data_tgp_no=1')
        assert '"data": [0, 1, 2, 3]' in self.body
        Spy.assert_ok(self.body, 'current_page', 1)
        Spy.assert_ok(self.body, 'first_item', 1)
        Spy.assert_ok(self.body, 'last_item', 4)

        self.request('/basic?data_tgp_no=2')
        assert '"data": [4, 5, 6, 7]' in self.body
        Spy.assert_ok(self.body, 'current_page', 2)
        Spy.assert_ok(self.body, 'first_item', 5)
        Spy.assert_ok(self.body, 'last_item', 8)

        self.request('/basic?data_tgp_no=3')
        assert '"data": [8, 9]' in self.body
        Spy.assert_ok(self.body, 'current_page', 3)
        Spy.assert_ok(self.body, 'first_item', 9)
        Spy.assert_ok(self.body, 'last_item', 10)

    def test_pagination_listlike(self):
        self.request('/listlike?data_tgp_no=2')
        assert '"data": [4, 5, 6, 7]' in self.body
        Spy.assert_ok(self.body, 'current_page', 2)
        Spy.assert_ok(self.body, 'first_item', 5)
        Spy.assert_ok(self.body, 'last_item', 8)

    def test_limit_override(self):
        # can't override limit
        self.request('/basic?data_tgp_limit=2')
        assert '"data": [0, 1, 2, 3]' in self.body

        # can't override limit with upper bound
        self.request('/max_limit?data_tgp_limit=9')
        assert '"data": [0, 1, 2, 3, 4, 5, 6]' in self.body
        Spy.assert_ok(self.body, 'page_count', 2)
        Spy.assert_ok(self.body, 'limit', 7)
        Spy.assert_ok(self.body, 'pages', xrange(1, 3))

        # can override limit
        self.request('/custom_limit?data_tgp_limit=2')
        assert '"data": [0, 1]' in self.body
        Spy.assert_ok(self.body, 'page_count', 5)
        Spy.assert_ok(self.body, 'limit', 2)
        Spy.assert_ok(self.body, 'pages', xrange(1, 6))

        # can override limit with upper bound
        self.request('/max_limit?data_tgp_limit=5')
        assert '"data": [0, 1, 2, 3, 4]' in self.body
        Spy.assert_ok(self.body, 'page_count', 2)
        Spy.assert_ok(self.body, 'limit', 5)
        Spy.assert_ok(self.body, 'pages', xrange(1, 3))

    def test_max_pages(self):
        self.request('/default_max_pages')
        assert '"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]' in self.body
        Spy.assert_ok(self.body, 'pages', xrange(1, 6))

        self.request('/default_max_pages?data_tgp_no=5')
        assert '"data": [40, 41, 42, 43, 44, 45, 46, 47, 48, 49]' in self.body
        Spy.assert_ok(self.body, 'pages', xrange(3, 8))

        self.request('/three_max_pages')
        assert '"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]' in self.body
        Spy.assert_ok(self.body, 'pages', xrange(1, 4))

        self.request('/three_max_pages?data_tgp_no=5')
        assert '"data": [40, 41, 42, 43, 44, 45, 46, 47, 48, 49]' in self.body
        Spy.assert_ok(self.body, 'pages', xrange(4, 7))

        # even 'max pages'
        self.request('/four_max_pages')
        assert '"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]' in self.body
        Spy.assert_ok(self.body, 'pages', xrange(1, 5))

        self.request('/four_max_pages?data_tgp_no=5')
        assert '"data": [40, 41, 42, 43, 44, 45, 46, 47, 48, 49]' in self.body
        Spy.assert_ok(self.body, 'pages', xrange(4, 8))

    def test_strict_parameters(self):
        config.update({'tg.strict_parameters': True})
        try:
            # check that paginate works with strict parameters as well
            self.request('/basic?data_tgp_no=2', status=200)
            assert '"data": [4, 5, 6, 7]' in self.body
            Spy.assert_ok(self.body, 'current_page', 2)
            self.request('/custom_limit?data_tgp_limit=2', status=200)
            assert '"data": [0, 1]' in self.body
            Spy.assert_ok(self.body, 'limit', 2)
            self.request('/default_max_pages?data_tgp_no=5', status=200)
            assert '"data": [40, 41, 42, ' in self.body
            Spy.assert_ok(self.body, 'pages', xrange(3, 8))
            # check that wrong and old style parameters are not accepted
            self.request('/basic?data_tgp_rubbish=2', status = 500)
            assert ("basic() got an unexpected keyword argument"
                " 'data_tgp_rubbish'") in self.body
            self.request('/basic?tg_paginate_no=2', status=500)
            assert ("basic() got an unexpected keyword argument"
                " 'tg_paginate_no'") in self.body
        finally:
            config.update({'tg.strict_parameters': False})

    def test_invalid_dynamic_limit(self):
        self.request('/invalid_dynamic', status=500)
        assert ('paginate: dynamic_limit (foobar) not found'
            ' in output dict') in self.body

    def test_dynamic_limit(self):
        self.request('/dynamic')
        assert '"data": [0, 1, 2, 3, 4, 5, 6]' in self.body

        self.request('/dynamic?data_tgp_limit=2')
        assert '"data": [0, 1, 2, 3, 4, 5, 6]' in self.body

    def test_multiple(self):
        self.request('/multiple')
        assert '"foo": [0, 1, 2, 3]' in self.body
        assert ('"bar": ["A", "B", "C", "D", "E",'
            ' "F", "G", "H", "I", "J"]') in self.body

        self.request('/multiple?foo_tgp_no=3')
        assert '"foo": [8, 9, 10, 11]' in self.body
        assert ('"bar": ["A", "B", "C", "D", "E",'
            ' "F", "G", "H", "I", "J"]') in self.body

        self.request('/multiple?bar_tgp_no=2')
        assert '"foo": [0, 1, 2, 3]' in self.body
        assert ('"bar": ["K", "L", "M", "N", "O",'
            ' "P", "Q", "R", "S", "T"]') in self.body

        self.request('/multiple?foo_tgp_no=2&bar_tgp_no=3')
        assert '"foo": [4, 5, 6, 7]' in self.body
        assert '"bar": ["U", "V", "W", "X", "Y", "Z"]' in self.body

    def test_out_of_bound_pages(self):
        for number in range(-3,1):
            self.request('/basic?data_tgp_no=%s' % number)
            assert '"data": [0, 1, 2, 3]' in self.body
            Spy.assert_ok(self.body, 'current_page', 1)
            Spy.assert_ok(self.body, 'first_item', 1)
            Spy.assert_ok(self.body, 'last_item', 4)

        for number in range(4, 7):
            self.request('/basic?data_tgp_no=%s' % number)
            assert '"data": [8, 9]' in self.body
            Spy.assert_ok(self.body, 'current_page', 3)
            Spy.assert_ok(self.body, 'first_item', 9)
            Spy.assert_ok(self.body, 'last_item', 10)

    def test_last_page(self):
        self.request('/basic?data_tgp_no=last')
        assert '"data": [8, 9]' in self.body
        Spy.assert_ok(self.body, 'current_page', 3)
        Spy.assert_ok(self.body, 'first_item', 9)
        Spy.assert_ok(self.body, 'last_item', 10)

    def test_href(self):
        self.request('/basic?data_tgp_no=0') # out of bound
        Spy.assert_ok(self.body, 'current_page', 1)
        Spy.assert_ok(self.body, 'href_first', None)
        Spy.assert_ok(self.body, 'href_prev', None)
        Spy.assert_ok(self.body, 'href_next',
            r"'/basic?data_tgp_no=2&data_tgp_limit=4'", raw=True)
        Spy.assert_ok(self.body, 'href_last',
            r"'/basic?data_tgp_no=last&data_tgp_limit=4'", raw=True)

        self.request('/basic?data_tgp_no=1')
        Spy.assert_ok(self.body, 'current_page', 1)
        Spy.assert_ok(self.body, 'href_first', None)
        Spy.assert_ok(self.body, 'href_prev', None)
        Spy.assert_ok(self.body, 'href_next',
            r"'/basic?data_tgp_no=2&data_tgp_limit=4'", raw=True)
        Spy.assert_ok(self.body, 'href_last',
            r"'/basic?data_tgp_no=last&data_tgp_limit=4'", raw=True)

        self.request('/basic?data_tgp_no=2')
        Spy.assert_ok(self.body, 'current_page', 2)
        Spy.assert_ok(self.body, 'href_first',
            r"'/basic?data_tgp_no=1&data_tgp_limit=4'", raw=True)
        Spy.assert_ok(self.body, 'href_prev',
            r"'/basic?data_tgp_no=1&data_tgp_limit=4'", raw=True)
        Spy.assert_ok(self.body, 'href_next',
            r"'/basic?data_tgp_no=3&data_tgp_limit=4'", raw=True)
        Spy.assert_ok(self.body, 'href_last',
            r"'/basic?data_tgp_no=last&data_tgp_limit=4'", raw=True)

        self.request('/basic?data_tgp_no=3')
        Spy.assert_ok(self.body, 'current_page', 3)
        Spy.assert_ok(self.body, 'href_first',
            r"'/basic?data_tgp_no=1&data_tgp_limit=4'", raw=True)
        Spy.assert_ok(self.body, 'href_prev',
            r"'/basic?data_tgp_no=2&data_tgp_limit=4'", raw=True)
        Spy.assert_ok(self.body, 'href_next', None)
        Spy.assert_ok(self.body, 'href_last', None)

        self.request('/basic?data_tgp_no=4') # out of bound!
        Spy.assert_ok(self.body, 'current_page', 3)
        Spy.assert_ok(self.body, 'href_first',
            r"'/basic?data_tgp_no=1&data_tgp_limit=4'", raw=True)
        Spy.assert_ok(self.body, 'href_prev',
            r"'/basic?data_tgp_no=2&data_tgp_limit=4'", raw=True)
        Spy.assert_ok(self.body, 'href_next', None)
        Spy.assert_ok(self.body, 'href_last', None)

        # empty data
        self.request('/empty')
        Spy.assert_ok(self.body, 'current_page', 1)
        Spy.assert_ok(self.body, 'href_first', None)
        Spy.assert_ok(self.body, 'href_prev', None)
        Spy.assert_ok(self.body, 'href_next', None)
        Spy.assert_ok(self.body, 'href_last', None)

    def test_with_webpath(self):
        config.update({'server.webpath': '/web/path'})
        try:
            self.request('/basic?data_tgp_no=2')
            Spy.assert_ok(self.body, 'current_page', 2)
            Spy.assert_ok(self.body, 'href_first',
                r"'/web/path/basic?data_tgp_no=1&data_tgp_limit=4'", raw=True)
            Spy.assert_ok(self.body, 'href_prev',
                r"'/web/path/basic?data_tgp_no=1&data_tgp_limit=4'", raw=True)
            Spy.assert_ok(self.body, 'href_next',
                r"'/web/path/basic?data_tgp_no=3&data_tgp_limit=4'", raw=True)
            Spy.assert_ok(self.body, 'href_last',
                r"'/web/path/basic?data_tgp_no=last&data_tgp_limit=4'", raw=True)
        finally:
            config.update({'server.webpath': ''})

    def test_empty_data(self):
        self.request('/empty')
        assert '"data": []' in self.body
        Spy.assert_ok(self.body, 'limit', 4)

    def test_zero_limit(self):
        self.request('/custom_limit?data_tgp_limit=0')
        assert '"data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]' in self.body
        Spy.assert_ok(self.body, 'page_count', 1)
        Spy.assert_ok(self.body, 'limit', 10)
        Spy.assert_ok(self.body, 'pages', xrange(1, 2))

    def test_empty_data_zero_limit(self):
        self.request('/empty?data_tgp_limit=0')
        assert '"data": []' in self.body
        Spy.assert_ok(self.body, 'page_count', 0)
        Spy.assert_ok(self.body, 'limit', 1)


#
# Test SQLAlchemy & SQLObject
#

class Occupation(object):
    pass

class User(object):
    pass

class Address(object):
    def __repr__(self):
        # using "[...]" instead of "<...>" avoids rendering "&lt;"
        return "[Address %r]" % self.id

class SOAddress(SQLObject):
    id = IntCol(),
    user_id = IntCol()
    street = StringCol()
    city = StringCol()

    def __repr__(self):
        # using "[...]" instead of "<...>" avoids rendering "&lt;"
        return "[Address %r]" % self.id

def create_tables():
    """Create tables filled with test data."""

    occupations_table = Table('occupations', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(20)))
    users_table = Table('users', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(20)),
        Column('occupation_id', Integer, ForeignKey("occupations.id")))
    addresses_table = Table('addresses', metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', Integer, ForeignKey("users.id")),
        Column('street', String(50)),
        Column('city', String(40)))

    mapper(Occupation, occupations_table)
    mapper(User, users_table, properties={
        'occupation' : relation(Occupation, lazy=False),
        'addresses': relation(Address, backref='user', lazy=False)})
    mapper(Address, addresses_table)

    metadata.create_all()

    occupations = (
        {'id': 1, 'name': 'Doctor'},
        {'id': 2, 'name': 'Actor'},
        {'id': 3, 'name': 'Programmer'})
    users = (
        {'id': 1, 'name': 'Smith', 'occupation_id': 1},
        {'id': 2, 'name': 'John', 'occupation_id': 2},
        {'id': 3, 'name': 'Fred', 'occupation_id': 2},
        {'id': 4, 'name': 'Albert', 'occupation_id': 3},
        {'id': 5, 'name': 'Nicole', 'occupation_id': None},
        {'id': 6, 'name': 'Sarah', 'occupation_id': None},
        {'id': 7, 'name': 'Walter', 'occupation_id': 1},
        {'id': 8, 'name': 'Bush', 'occupation_id': None});
    addresses = (
        {'id': 1, 'user_id': None, 'street': 'street P', 'city': 'city X'},
        {'id': 2, 'user_id': 2, 'street': 'street B', 'city': 'city Z'},
        {'id': 3, 'user_id': 4, 'street': 'street C', 'city': 'city X'},
        {'id': 4, 'user_id': 1, 'street': 'street D', 'city': 'city Y'},
        {'id': 5, 'user_id': None, 'street': 'street E', 'city': 'city Z'},
        {'id': 6, 'user_id': 1, 'street': 'street F', 'city': 'city Z'},
        {'id': 7, 'user_id': 3, 'street': 'street G', 'city': 'city Y'},
        {'id': 8, 'user_id': 7, 'street': 'street H', 'city': 'city Y'},
        {'id': 9, 'user_id': 1, 'street': 'street I', 'city': 'city X'},
        {'id': 10, 'user_id': 6, 'street': 'street J', 'city': 'city X'},
        {'id': 11, 'user_id': 3, 'street': 'street K', 'city': 'city Z'},
        {'id': 12, 'user_id': 2, 'street': 'street L', 'city': 'city X'},
        {'id': 13, 'user_id': 8, 'street': 'street M', 'city': 'city X'},
        {'id': 14, 'user_id': 5, 'street': 'street N', 'city': 'city Y'},
        {'id': 15, 'user_id': 1, 'street': 'street O', 'city': 'city Y'},
        {'id': 16, 'user_id': 3, 'street': 'street A', 'city': 'city X'});

    metadata.bind.execute(occupations_table.insert(), occupations)
    metadata.bind.execute(users_table.insert(), users)
    metadata.bind.execute(addresses_table.insert(), addresses)

    SOAddress.createTable()

    # SQLObject tests will need only "addresses"
    for kw in addresses:
        SOAddress(**kw)

def drop_tables():
    metadata.drop_all()


class TestDatabasePagination(TestPagination):

    class MyRoot(RootController):

        def __common(self, method=None):
            if method == 'Q':
                data = session.query(Address)
            elif method == 'QA':
                data = session.query(Address).all()
            elif method == 'SO':
                data = SOAddress.select()
            elif method == 'SL':
                data = list(SOAddress.select())
            else:
                raise ValueError('Invalid method %r' % method)

            spy = Spy(var_name='data', pages=xrange(1, 3),
                      limit=10, page_count=2, order=None, row_count=16)
            return dict(data=data, spy=spy)

        # default_order = basestring
        basic1 = paginate('data', default_order='id')(__common)
        basic1 = expose('turbogears.tests.paginate')(basic1)

        # default_order = list
        basic2 = paginate('data', default_order=['id'])(__common)
        basic2 = expose('turbogears.tests.paginate')(basic2)

        # default_order = basestring
        reversed1 = paginate('data', default_order='-id')(__common)
        reversed1 = expose('turbogears.tests.paginate')(reversed1)

        # default_order = list
        reversed2 = paginate('data', default_order=['-id'])(__common)
        reversed2 = expose('turbogears.tests.paginate')(reversed2)

        # +/+
        default_compound_ordering1 = paginate('data',
            default_order=['city', 'street'])(__common)
        default_compound_ordering1 = expose('turbogears.tests.paginate')(
            default_compound_ordering1)

        # +/-
        default_compound_ordering2 = paginate('data',
            default_order=['city', '-street'])(__common)
        default_compound_ordering2 = expose('turbogears.tests.paginate')(
            default_compound_ordering2)

        # -/+
        default_compound_ordering3 = paginate('data',
            default_order=['-city', 'street'])(__common)
        default_compound_ordering3 = expose('turbogears.tests.paginate')(
            default_compound_ordering3)

        # -/-
        default_compound_ordering4 = paginate('data',
            default_order=['-city', '-street'])(__common)
        default_compound_ordering4 = expose('turbogears.tests.paginate')(
            default_compound_ordering4)

        @expose('turbogears.tests.paginate')
        @paginate('data', default_order='id')
        def related(self, join=None):
            # only SA Query
            data = session.query(Address)
            if join:
                join = str(join).split(',')
                if hasattr(Address, 'c'): # SQLAlchemy < 0.5
                    join = [join]
                data = data.outerjoin(*join)

            spy = Spy(var_name='data', pages=xrange(1, 3),
                      limit=10, page_count=2, order=None, row_count=16)
            return dict(data=data, spy=spy)

        @expose('turbogears.tests.paginate')
        @paginate('data', default_order="id", limit=0)
        def zero_limit(self, method=None):
            if method == 'Q':
                data = session.query(Address)
            elif method == 'QA':
                data = session.query(Address).all()
            elif method == 'SO':
                data = SOAddress.select()
            elif method == 'SL':
                data = list(SOAddress.select())
            else:
                raise Exception("Invalid method")

            spy = Spy(var_name='data', pages=xrange(1, 2),
                      limit=16, page_count=1, order=None, row_count=16)
            return dict(data=data, spy=spy)

        @expose('turbogears.tests.paginate')
        @paginate('data', default_order="id")
        def empty_with_groupby(self):
            data = session.query(Address)
            try:
                data = data.filter(
                    Address.c.id < 0).group_by(Address.c.user_id)
            except AttributeError: # SQLAlchemy >= 0.5
                data = data.filter(Address.id < 0).group_by(Address.user_id)
            spy = Spy(var_name='data', pages=xrange(1, 1),
                      limit=10, page_count=0, order=None, row_count=0)
            return dict(data=data, spy=spy)


    def assert_order(self, *args):
        expr = 'data="%s"' % ''.join(['[Address %r]' % x for x in args])
        assert expr in self.body, "expected %s" % expr

    def test_basic(self):
        for test in 'basic1', 'basic2':
            for method in query_methods:
                self.request('/%s?method=%s' % (test, method))
                self.assert_order(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                Spy.assert_ok(self.body, 'current_page', 1)
                Spy.assert_ok(self.body, 'first_item', 1)
                Spy.assert_ok(self.body, 'last_item', 10)
                Spy.assert_ok(self.body, 'ordering', ['id'])

                self.request('/%s?method=%s&data_tgp_no=2' % (test, method))
                self.assert_order(11, 12, 13, 14, 15, 16)
                Spy.assert_ok(self.body, 'current_page', 2)
                Spy.assert_ok(self.body, 'first_item', 11)
                Spy.assert_ok(self.body, 'last_item', 16)
                Spy.assert_ok(self.body, 'ordering', ['id'])

    def test_ordering(self):
        for test in 'basic1', 'basic2':
            for method in query_methods:
                self.request('/%s?method=%s&data_tgp_ordering=%s'
                    % (test, method, 'street'))
                self.assert_order(16, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                Spy.assert_ok(self.body, 'current_page', 1)
                Spy.assert_ok(self.body, 'first_item', 1)
                Spy.assert_ok(self.body, 'last_item', 10)
                Spy.assert_ok(self.body, 'ordering', ['street'])

                self.request('/%s?method=%s&data_tgp_no=2&data_tgp_ordering=%s'
                    % (test, method, 'street'))
                self.assert_order(11, 12, 13, 14, 15, 1)
                Spy.assert_ok(self.body, 'current_page', 2)
                Spy.assert_ok(self.body, 'first_item', 11)
                Spy.assert_ok(self.body, 'last_item', 16)
                Spy.assert_ok(self.body, 'ordering', ['street'])

    def test_strict_parameters(self):
        config.update({'tg.strict_parameters': True})
        try:
            # check that paginate ordering works with strict parameters as well
            self.request('/basic1?method=Q&data_tgp_ordering=street',
                status=200)
            self.assert_order(16, 2, 3, 4, 5, 6, 7, 8, 9, 10)
            Spy.assert_ok(self.body, 'ordering', ['street'])
            # check that old style ordering is not accepted any more
            self.request('/basic1?method=Q&tg_paginate_ordering=street',
                status=500)
            assert ("got an unexpected keyword argument"
                " 'tg_paginate_ordering'") in self.body
        finally:
            config.update({'tg.strict_parameters': False})

    def test_reversed(self):
        for test in 'reversed1', 'reversed2':
            for method in query_methods:
                self.request('/%s?method=%s' % (test, method))
                self.assert_order(16, 15, 14, 13, 12, 11, 10, 9, 8, 7)
                Spy.assert_ok(self.body, 'current_page', 1)
                Spy.assert_ok(self.body, 'first_item', 1)
                Spy.assert_ok(self.body, 'last_item', 10)
                Spy.assert_ok(self.body, 'ordering', ['-id'])

                self.request('/%s?method=%s&data_tgp_no=2' % (test, method))
                self.assert_order(6, 5, 4, 3, 2, 1)
                Spy.assert_ok(self.body, 'current_page', 2)
                Spy.assert_ok(self.body, 'first_item', 11)
                Spy.assert_ok(self.body, 'last_item', 16)
                Spy.assert_ok(self.body, 'ordering', ['-id'])

    def test_reverse_ordering(self):
        for test in 'basic1', 'basic2':
            for method in query_methods:
                self.request('/%s?method=%s&data_tgp_ordering=%s'
                    % (test, method, '-street'))
                self.assert_order(1, 15, 14, 13, 12, 11, 10, 9, 8, 7)
                Spy.assert_ok(self.body, 'ordering', ['-street'])

                self.request('/%s?method=%s&data_tgp_no=2&data_tgp_ordering=%s'
                    % (test, method, '-street'))
                self.assert_order(6, 5, 4, 3, 2, 16)
                Spy.assert_ok(self.body, 'ordering', ['-street'])

    def test_compound_ordering(self):
        for test in 'basic1', 'basic2':
            for method in query_methods:
                # +/+
                self.request('/%s?method=%s&data_tgp_ordering=%s'
                    % (test, method, quote('city,street')))
                self.assert_order(16, 3, 9, 10, 12, 13, 1, 4, 7, 8)
                Spy.assert_ok(self.body, 'ordering', ['city', 'street'])

                self.request('/%s?method=%s&data_tgp_no=2&data_tgp_ordering=%s'
                    % (test, method, quote('city,street')))
                self.assert_order(14, 15, 2, 5, 6, 11)
                Spy.assert_ok(self.body, 'ordering', ['city', 'street'])

                # +/-
                self.request('/%s?method=%s&data_tgp_ordering=%s'
                    % (test, method, quote('city,-street')))
                self.assert_order(1, 13, 12, 10, 9, 3, 16, 15, 14, 8)
                Spy.assert_ok(self.body, 'ordering', ['city', '-street'])

                self.request('/%s?method=%s&data_tgp_no=2&data_tgp_ordering=%s'
                    % (test, method, quote('city,-street')))
                self.assert_order(7, 4, 11, 6, 5, 2)
                Spy.assert_ok(self.body, 'ordering', ['city', '-street'])

                # -/+
                self.request('/%s?method=%s&data_tgp_ordering=%s'
                    % (test, method, quote('-city,street')))
                self.assert_order(2, 5, 6, 11, 4, 7, 8, 14, 15, 16)
                Spy.assert_ok(self.body, 'ordering', ['-city', 'street'])

                self.request('/%s?method=%s&data_tgp_no=2&data_tgp_ordering=%s'
                    % (test, method, quote('-city,street')))
                self.assert_order(3, 9, 10, 12, 13, 1)
                Spy.assert_ok(self.body, 'ordering', ['-city', 'street'])

                # -/-
                self.request('/%s?method=%s&data_tgp_ordering=%s'
                    % (test, method, quote('-city,-street')))
                self.assert_order(11, 6, 5, 2, 15, 14, 8, 7, 4, 1)
                Spy.assert_ok(self.body, 'ordering', ['-city', '-street'])

                self.request('/%s?method=%s&data_tgp_no=2&data_tgp_ordering=%s'
                    % (test, method, quote('-city,-street')))
                self.assert_order(13, 12, 10, 9, 3, 16)
                Spy.assert_ok(self.body, 'ordering', ['-city', '-street'])

    def test_default_compound_ordering_1(self):
        # +/+
        for method in query_methods:
            self.request('/default_compound_ordering1?method=%s' % method)
            self.assert_order(16, 3, 9, 10, 12, 13, 1, 4, 7, 8)
            Spy.assert_ok(self.body, 'ordering', ['city', 'street'])

            self.request('/default_compound_ordering1?method=%s&data_tgp_no=2'
                % method)
            self.assert_order(14, 15, 2, 5, 6, 11)
            Spy.assert_ok(self.body, 'ordering', ['city', 'street'])

    def test_default_compound_ordering_2(self):
        # +/-
        for method in query_methods:
            self.request('/default_compound_ordering2?method=%s' % method)
            self.assert_order(1, 13, 12, 10, 9, 3, 16, 15, 14, 8)
            Spy.assert_ok(self.body, 'ordering', ['city', '-street'])

            self.request('/default_compound_ordering2?method=%s&data_tgp_no=2'
                % method)
            self.assert_order(7, 4, 11, 6, 5, 2)
            Spy.assert_ok(self.body, 'ordering', ['city', '-street'])

    def test_default_compound_ordering_3(self):
        # -/+
        for method in query_methods:
            self.request('/default_compound_ordering3?method=%s' % method)
            self.assert_order(2, 5, 6, 11, 4, 7, 8, 14, 15, 16)
            Spy.assert_ok(self.body, 'ordering', ['-city', 'street'])

            self.request('/default_compound_ordering3?method=%s&data_tgp_no=2'
                % method)
            self.assert_order(3, 9, 10, 12, 13, 1)
            Spy.assert_ok(self.body, 'ordering', ['-city', 'street'])

    def test_default_compound_ordering_4(self):
        # -/-
        for method in query_methods:
            self.request('/default_compound_ordering4?method=%s' % method)
            self.assert_order(11, 6, 5, 2, 15, 14, 8, 7, 4, 1)
            Spy.assert_ok(self.body, 'ordering', ['-city', '-street'])

            self.request('/default_compound_ordering4?method=%s&data_tgp_no=2'
                % method)
            self.assert_order(13, 12, 10, 9, 3, 16)
            Spy.assert_ok(self.body, 'ordering', ['-city', '-street'])

    def test_related_objects_ordering_level_1(self):
        # +/+
        self.request('/related?data_tgp_ordering=%s' % quote('user.name,id'))
        self.assert_order(1, 5, 3, 13, 7, 11, 16, 2, 12, 14)
        Spy.assert_ok(self.body, 'ordering', ['user.name', 'id'])

        self.request('/related?data_tgp_no=2&data_tgp_ordering=%s'
            % quote('user.name,id'))
        self.assert_order(10, 4, 6, 9, 15, 8)
        Spy.assert_ok(self.body, 'ordering', ['user.name', 'id'])

        # +/-
        self.request('/related?data_tgp_ordering=%s' % quote('user.name,-id'))
        self.assert_order(5, 1, 3, 13, 16, 11, 7, 12, 2, 14)
        Spy.assert_ok(self.body, 'ordering', ['user.name', '-id'])

        self.request('/related?data_tgp_no=2&data_tgp_ordering=%s'
            % quote('user.name,-id'))
        self.assert_order(10, 15, 9, 6, 4, 8)
        Spy.assert_ok(self.body, 'ordering', ['user.name', '-id'])

        # -/+
        self.request('/related?data_tgp_ordering=%s' % quote('-user.name,id'))
        self.assert_order(8, 4, 6, 9, 15, 10, 14, 2, 12, 7)
        Spy.assert_ok(self.body, 'ordering', ['-user.name', 'id'])

        self.request('/related?data_tgp_no=2&data_tgp_ordering=%s'
            % quote('-user.name,id'))
        self.assert_order(11, 16, 13, 3, 1, 5)
        Spy.assert_ok(self.body, 'ordering', ['-user.name', 'id'])

        # -/-
        self.request('/related?data_tgp_ordering=%s' % quote('-user.name,-id'))
        self.assert_order(8, 15, 9, 6, 4, 10, 14, 12, 2, 16)
        Spy.assert_ok(self.body, 'ordering', ['-user.name', '-id'])

        self.request('/related?data_tgp_no=2&data_tgp_ordering=%s'
            % quote('-user.name,-id'))
        self.assert_order(11, 7, 13, 3, 5, 1)
        Spy.assert_ok(self.body, 'ordering', ['-user.name', '-id'])

    def test_related_objects_ordering_level_2(self):
        # +/+
        self.request('/related?data_tgp_ordering=%s'
            % quote('user.occupation.name,id'))
        self.assert_order(1, 5, 10, 13, 14, 2, 7, 11, 12, 16)
        Spy.assert_ok(self.body, 'ordering', ['user.occupation.name', 'id'])

        self.request('/related?data_tgp_no=2&data_tgp_ordering=%s'
            % quote('user.occupation.name,id'))
        self.assert_order(4, 6, 8, 9, 15, 3)
        Spy.assert_ok(self.body, 'ordering', ['user.occupation.name', 'id'])

        # +/-
        self.request('/related?data_tgp_ordering=%s'
            % quote('user.occupation.name,-id'))
        self.assert_order(14, 13, 10, 5, 1, 16, 12, 11, 7, 2)
        Spy.assert_ok(self.body, 'ordering', ['user.occupation.name', '-id'])

        self.request('/related?data_tgp_no=2&data_tgp_ordering=%s'
            % quote('user.occupation.name,-id'))
        self.assert_order(15, 9, 8, 6, 4, 3)
        Spy.assert_ok(self.body, 'ordering', ['user.occupation.name', '-id'])

        # -/+
        self.request('/related?data_tgp_ordering=%s'
            % quote('-user.occupation.name,id'))
        self.assert_order(3, 4, 6, 8, 9, 15, 2, 7, 11, 12)
        Spy.assert_ok(self.body, 'ordering', ['-user.occupation.name', 'id'])

        self.request('/related?data_tgp_no=2&data_tgp_ordering=%s'
            % quote('-user.occupation.name,id'))
        self.assert_order(16, 1, 5, 10, 13, 14)
        Spy.assert_ok(self.body, 'ordering', ['-user.occupation.name', 'id'])

        # -/-
        self.request('/related?data_tgp_ordering=%s'
            % quote('-user.occupation.name,-id'))
        self.assert_order(3, 15, 9, 8, 6, 4, 16, 12, 11, 7)
        Spy.assert_ok(self.body, 'ordering', ['-user.occupation.name', '-id'])

        self.request('/related?data_tgp_no=2&data_tgp_ordering=%s'
            % quote('-user.occupation.name,-id'))
        self.assert_order(2, 14, 13, 10, 5, 1)
        Spy.assert_ok(self.body, 'ordering', ['-user.occupation.name', '-id'])

    def test_related_objects_with_explicit_join(self):
        # +/+
        self.request('/related?join=%s&data_tgp_ordering=%s'
            % (quote('user,occupation'), quote('user.occupation.name,id')))
        self.assert_order(1, 5, 10, 13, 14, 2, 7, 11, 12, 16)
        Spy.assert_ok(self.body, 'ordering', ['user.occupation.name', 'id'])

        # -/-
        self.request('/related?join=%s&data_tgp_ordering=%s'
            % (quote('user,occupation'), quote('-user.occupation.name,-id')))
        self.assert_order(3, 15, 9, 8, 6, 4, 16, 12, 11, 7)
        Spy.assert_ok(self.body, 'ordering', ['-user.occupation.name', '-id'])

    def test_zero_limit(self):
        for method in query_methods:
            self.request('/zero_limit?method=%s' % method)
            self.assert_order(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)

    def test_ticket_1641(self):
        self.request('/empty_with_groupby')
        self.assert_order()


def setup_module():
    global _sa_dburi, _so_dburi
    _so_dburi = config.get('sqlobject.dburi', 'sqlite:///:memory:')
    _sa_dburi = config.get('sqlalchemy.dburi', 'sqlite:///:memory:')
    # sqlalchemy setup
    database.set_db_uri("sqlite:///:memory:", 'sqlalchemy')
    sqlalchemy_cleanup()
    bind_metadata()

    # sqlobject setup
    database.set_db_uri("sqlite:///:memory:", 'sqlobject')

    create_tables()
    hub.commit()

def teardown_module():
    drop_tables()
    sqlalchemy_cleanup()
    config.update({'sqlalchemy.dburi': _sa_dburi, 'sqlobject.dburi': _so_dburi})
