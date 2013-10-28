"""Tests for SQLObject database operations"""

from turbogears import database, testutil
from sqlobject import dbconnection
import cherrypy
from turbogears.controllers import RootController


_using_sa = database._using_sa

def setup(module):
    # turn off SQLAlchemy for these tests
    global _using_sa
    _using_sa = database._using_sa
    database._using_sa = False

def teardown(module):
    database._using_sa = _using_sa


def test_registry():
    """hubs appear in a registry"""
    hub = database.AutoConnectHub("sqlite:///:memory:")
    try:
        assert hub in database.hub_registry
    finally:
        database.hub_registry.clear()


def test_alwaysTransaction():
    """hub.getConnection always returns a Transaction"""
    hub = database.AutoConnectHub("sqlite:///:memory:")
    try:
        assert isinstance(hub.getConnection(), dbconnection.Transaction)
        database.end_all()
        assert not isinstance(hub.threadingLocal.connection, dbconnection.Transaction)
    finally:
        database.hub_registry.clear()


class DummyRedirect(Exception):
    pass


class DatabaseStandIn:

    committed = False
    rolled_back = False
    ended = False
    successful_called = False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def end(self):
        self.ended = True

    def successful(self):
        self.successful_called = True

    def failure(self):
        self.failure_called = True
        raise Warning("Oh my!")

    def redirect(self):
        self.redirect_called = True
        raise cherrypy.HTTPRedirect("/")


def test_good_transaction():
    """successful runs automatically commit"""
    dsi = DatabaseStandIn()
    database.hub_registry.add(dsi)
    try:
        database.run_with_transaction(dsi.successful)
        assert dsi.successful_called
        assert dsi.committed
        assert dsi.ended
    finally:
        database.hub_registry.clear()


def test_bad_transaction():
    """failed runs automatically rollback"""
    dsi = DatabaseStandIn()
    database.hub_registry.add(dsi)
    try:
        try:
            database.run_with_transaction(dsi.failure)
            assert False, "exception should have been raised"
        except:
            pass
        assert dsi.failure_called
        assert dsi.rolled_back
        assert dsi.ended
    finally:
        database.hub_registry.clear()


def test_redirection():
    """Redirects count as successful runs, not failures"""
    dsi = DatabaseStandIn()
    database.hub_registry.add(dsi)
    #The real cherrypy redirect is only available within a request,
    # so monkey-patch in this dummy.
    _http_redirect = cherrypy.HTTPRedirect
    cherrypy.HTTPRedirect = DummyRedirect
    try:
        try:
            database.run_with_transaction(dsi.redirect)
        except cherrypy.HTTPRedirect:
            pass
        assert dsi.redirect_called
        assert dsi.committed
        assert dsi.ended
    finally:
        database.hub_registry.clear()
        cherrypy.HTTPRedirect = _http_redirect


def test_so_to_dict():
    """Conversion to dictionary works properly"""
    hub = database.AutoConnectHub("sqlite:///:memory:")
    try:
        from sqlobject import IntCol
        from sqlobject.inheritance import InheritableSQLObject

        class Parent(InheritableSQLObject):
            _connection = hub
            a   = IntCol()

        class Child(Parent):
            _connection = hub
            b   = IntCol()

        Parent.createTable()
        Child.createTable()
        p =  Parent(a=1)
        c =  Child(a=1, b=2)

        p_dict = database.so_to_dict(p)
        assert p_dict['a'] == 1

        c_dict = database.so_to_dict(c)
        assert c_dict['a'] == 1
        assert c_dict['b'] == 2
        assert None == c_dict.get('childName', None)
        assert None == p_dict.get('childName', None)
    finally:
        database.hub_registry.clear()
