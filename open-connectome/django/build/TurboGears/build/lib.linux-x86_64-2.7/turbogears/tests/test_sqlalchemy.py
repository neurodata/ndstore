"""Tests for SQLAlchemy support"""

import cherrypy, os, threading, turbogears

from sqlalchemy import Table, Column, ForeignKey, Integer, String
from sqlalchemy.orm import mapper, relation

from turbogears import config, redirect, expose, errorhandling
from turbogears.database import metadata, session, bind_metadata, get_metadata
from turbogears.controllers import RootController
from turbogears.testutil import make_app, sqlalchemy_cleanup, \
    start_server, stop_server


# Fixture

class User(object):
    def __repr__(self):
        return "<User: '%s', name: '%s', password: '%s'>" % (
                self.user_id, self.user_name, self.password)

class Person(object):
    def __repr__(self):
        return "<Person: '%s', name: '%s', addresses: '%s'>" % (
                self.id, self.name, self.addresses)

class Address(object):
    def __repr__(self):
        return "<Address: '%s', where: '%s', city: '%s', person: '%s'>" % (
                self.id, self.address, self.city, self.person_id)

class Test(object):
    pass


def setup_module():
    global users_table, test_table, multi_table, fresh_multi_table

    config.update({
        'sqlalchemy.dburi': 'sqlite:///:memory:',
        'fresh.dburi': 'sqlite:///freshtest.db',
    })

    if os.path.exists('freshtest.db'):
        os.unlink('freshtest.db')
    fresh_metadata = get_metadata('fresh')
    if metadata.is_bound():
        metadata.bind = None
    bind_metadata()
    metadata.bind.echo = True
    fresh_metadata.bind.echo = True

    users_table = Table("users", metadata,
        Column("user_id", Integer, primary_key=True),
        Column("user_name", String(40)),
        Column("password", String(10)))
    persons_table = Table("persons", metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(40)))
    addresses_table = Table("addresses", metadata,
            Column("id", Integer, primary_key=True),
            Column("address", String(40)),
            Column("city", String(40)),
            Column("person_id", Integer, ForeignKey(persons_table.c.id)))
    multi_table = Table('multi', metadata,
        Column('id', Integer, primary_key=True))

    metadata.create_all()

    test_table = Table("test", fresh_metadata,
        Column("id", Integer, primary_key=True),
        Column("val", String(40)))
    fresh_multi_table = Table('multi', fresh_metadata,
        Column('id', Integer, primary_key=True))

    fresh_metadata.create_all()

    mapper(User, users_table)
    mapper(Person, persons_table)
    mapper(Address, addresses_table, properties=dict(
        person=relation(Person, backref='addresses')))
    mapper(Test, test_table)

    start_server()

def teardown_module():
    fresh_metadata = get_metadata('fresh')
    fresh_metadata.drop_all()
    fresh_metadata.bind.dispose()
    metadata.drop_all()
    sqlalchemy_cleanup()
    if os.path.exists('freshtest.db'):
        os.unlink('freshtest.db')

    stop_server()


# Database tests

def test_query_in_session():
    i = users_table.insert()
    i.execute(user_name="globbo", password="thegreat!")
    query = session.query(User)
    globbo = query.filter_by(user_name="globbo").one()
    assert globbo.password == "thegreat!"
    users_table.delete().execute()

def test_create_and_query():
    i = users_table.insert()
    i.execute(user_name="globbo", password="thegreat!")
    s = users_table.select()
    r = s.execute()
    assert len(r.fetchall()) == 1
    users_table.delete().execute()

def test_multi_db():
    multi_table.insert().execute(id=1)
    fresh_multi_table.insert().execute(id=2)
    assert multi_table.select().execute().fetchall()[0][0] == 1
    assert fresh_multi_table.select().execute().fetchall()[0][0] == 2


# Exception handling

class MyRoot(RootController):
    """A small root controller for our exception handling tests"""

    @expose()
    def no_error(self, name):
        """Test controller"""
        person = Person()
        person.name = name
        session.add(person)
        raise redirect("/someconfirmhandler")

    def e_handler(self, id, tg_exceptions=None):
        """Test error handler

        This handler is called KARL25 and all returns from it
        will be marked with this name :)

        """
        msg = "KARL25 responding\n"
        msg += "user with id: '%s' should not be saved.\n" % id
        msg += "An exception occurred: %r (%s)" % ((tg_exceptions,)*2)
        return dict(msg=msg)

    @expose()
    @errorhandling.exception_handler(e_handler)
    def create_person(self, id,
            docom=0, doerr=0, doflush=0, name="John Doe"):
        """Test controller"""
        person = Person()
        person.id, person.name = int(id), name
        session.add(person)
        if int(docom) == 1:
            cherrypy.request.sa_transaction.commit()
        if int(doerr) == 1:
            raise Exception('User generated exception')
        elif int(doerr) == 2:
            raise turbogears.redirect('/')
        if int(doflush):
            try:
                session.flush()
            except Exception:
                if int(doflush) == 1:
                    raise
        return "No exceptions occurred"


def test_implicit_trans_no_error():
    """If a controller runs sucessfully, the transaction is commited."""
    app = make_app(MyRoot)
    response = app.get('/no_error?name=A.%20Dent')
    arthur = session.query(Person).filter_by(name="A. Dent").first()
    assert 'someconfirmhandler' in response, \
        'The no error should have redirected to someconfirmhandler'
    assert arthur is not None, 'Person arthur should have been saved!'
    assert arthur.name == "A. Dent", 'Person arthur should be named "A. Dent"'

def test_raise_sa_exception():
    """If a controller causes an SA exception, it is raised properly."""
    app = make_app(MyRoot)
    response = app.get('/create_person?id=20')
    assert 'No exceptions occurred' in response
    response = app.get('/create_person?id=20', status=500)
    assert 'KARL25' not in response, \
        'Exception should NOT have been handled by our handler'
    assert 'IntegrityError' in response, \
        'The page should have displayed a database integrity error'

def test_user_exception():
    """If a controller raises an exception, transactions are rolled back."""
    app = make_app(MyRoot)
    response = app.get('/create_person?id=19&docom=0&doerr=1&name=Martin%20GAL')
    assert 'KARL25' in response, \
        'The exception handler should have answered us'
    p = session.query(Person).get(19)
    assert p is None, \
        'This Person should have been rolled back: %s' % p

def test_user_redirect():
    """If a controller redirects, transactions are committed."""
    app = make_app(MyRoot)
    app.get('/create_person?id=22&doerr=2')
    assert session.query(Person).get(22) is not None, \
        'The controller only redirected, the Person should have been saved'

def test_cntrl_commit():
    """It's safe to commit a transaction in the controller."""
    app = make_app(MyRoot)
    response = app.get('/create_person?id=23&docom=1')
    assert 'InvalidRequestError' not in response
    assert session.query(Person).get(23) is not None, \
        'The Person 23 should have been saved during commit inside controller'

def test_cntrl_commit2():
    """A commit inside the controller is not rolled back by the exception."""
    app = make_app(MyRoot)
    response = app.get('/create_person?id=24&docom=1&doerr=1')
    assert 'InvalidRequestError' not in response
    assert session.query(Person).get(24) is not None, \
        'The Person 24 should have been saved during commit' \
        ' inside controller and not rolled back'

def test_cntrl_flush():
    """It's safe to flush in the controller."""
    app = make_app(MyRoot)
    response = app.get('/create_person?id=25&doflush=1')
    assert 'No exceptions occurred' in response
    response = app.get('/create_person?id=25&doflush=0', status=500)
    assert 'IntegrityError' in response
    response = app.get('/create_person?id=25&doflush=1')
    assert 'IntegrityError' in response
    response = app.get('/create_person?id=25&doflush=2')
    assert 'No exceptions occurred' in response


# Exception handling with rollback

class RbRoot(RootController):
    """A small root controller for our transaction rollback tests"""

    def handerr(self, id):
        """Test error handler.

        This handler will receive exceptions and create a user with id+1
        so we can see if the exception was caught correctly.

        """
        if not id == 'XX':
            user = User()
            user.user_id = int(id) + 1
            session.add(user)
            session.flush()
        msg = 'KARL27 responding'
        return dict(msg=msg)

    @expose()
    @errorhandling.exception_handler(handerr)
    def doerr(self, id, dorb=0):
        """Test controller that raises an error.

        This controller will raise an exception after trying to create
        a new User. This new user should not be in the database at the end
        because the rollback should make it disappear.

        dorb is a flag to check that if a rollback occurs inside the
        controller code, the exception does not cause problems.

        """
        user = User()
        user.user_id = int(id)
        session.add(user)
        session.flush()
        if int(dorb) == 1:
            session.rollback()
        raise Exception('test')


def test_exc_rollback():
    """An exception within a controller method causes a rollback.

    Try to create a user that should rollback because of an exception
    so user 25 should not exist, but user 26 should be present since it
    is created by the exception handler.

    """
    app = make_app(RbRoot)
    response = app.get('/doerr?id=26')
    assert 'KARL27' in response, 'Exception handler should have answered'
    assert session.query(User).get(26) is None
    assert session.query(User).get(27) is not None

def test_exc_rollback2():
    """An exception within a controller method causes a rollback.

    Try to create a user that should rollback because of an exception
    so user XX should not exist.

    """
    app = make_app(RbRoot)
    response = app.get('/doerr?id=XX')
    assert 'KARL27' in response, 'Exception handler should have answered'
    assert session.query(User).get('XX') is None

def test_exc_done_rollback():
    """No problems with error handler if controller manually rollbacks."""
    app = make_app(RbRoot)
    response = app.get('/doerr?id=28&dorb=1')
    assert 'KARL27' in response, 'Exception handler should have answered'
    assert session.query(User).get(28) is None
    assert session.query(User).get(29) is not None


# Session freshness tests

class FreshRoot(RootController):
    """A small root controller for our session freshness tests"""

    @expose()
    def test1(self):
        assert session.query(Test).get(1).val == 'a'
        return dict()

    @expose()
    def test2(self):
        session.query(Test).get(1).val = 'b'
        return dict()

    @expose()
    def test3(self):
        assert session.query(Test).get(1).val == 'b'
        return dict()


def test_session_freshness():
    """Check for session freshness.

    Changes made to the data in thread B should be reflected in thread A.

    """
    test_table.insert().execute(dict(id=1, val='a'))
    app = make_app(FreshRoot)
    response = app.get('/test1', status = 200)
    assert 'AssertionError' not in response
    # Call test2 in a different thread
    class ThreadB(threading.Thread):
        def run(self):
            response = app.get('/test2', status=200)
            assert 'AssertionError' not in response
    thrdb = ThreadB()
    thrdb.start()
    thrdb.join()
    response = app.get('/test3', status=200)
    assert 'AssertionError' not in response
