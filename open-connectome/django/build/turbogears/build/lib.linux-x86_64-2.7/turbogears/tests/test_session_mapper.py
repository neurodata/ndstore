"""Unit tests for turbogears.database.session_mapper."""

import unittest

from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import clear_mappers
try:
    from sqlalchemy.exc import ArgumentError
except ImportError: # SQLAlchemy < 0.5
    from sqlalchemy.exceptions import ArgumentError


from turbogears import config
from turbogears.database import (bind_metadata, metadata,
    session, session_mapper, set_db_uri)


class User(object):
    pass


class OldUser:
    pass


class SecretUser(User):

    def __init__(self, user_id, user_name):
        self.user_id = user_id
        self.user_name = user_name.lower()
        self.password = 'secret'


class RawUser(object):
    pass


class TestSessionMapper(unittest.TestCase):

    def setUp(self):
        """Set database configuration and set up database.
        """
        self.sa_dburi = config.get('sqlalchemy.dburi')
        set_db_uri('sqlite:///:memory:', 'sqlalchemy')
        bind_metadata()
        self.users_table = Table("users", metadata,
            Column("user_id", Integer, primary_key=True),
            Column("user_name", String(40)),
            Column("password", String(10)))
        metadata.create_all()

    def tearDown(self):
        """Clear database configuration and drop database.
        """
        try:
            session.expunge_all()
        except:
            session.clear()
        clear_mappers()
        metadata.drop_all()
        metadata.clear()
        set_db_uri(self.sa_dburi, 'sqlalchemy')

    def test_query_attribute(self):
        """Object mapped with session-aware mapper have 'query' attribute."""
        session_mapper(User, self.users_table)
        assert hasattr(User, 'query')
        assert hasattr(User.query, 'filter')

    def test_contructor(self):
        """Mapped objects have constructor which takes attributes as kw args."""
        session_mapper(User, self.users_table)
        test_user = User(user_id=1, user_name='Falken', password='Joshua')
        assert test_user.user_id == 1
        assert test_user.user_name == 'Falken'
        assert test_user.password == 'Joshua'

    def test_old_contructor(self):
        """Mapped old-style classes should work or give a proper error."""
        try:
            session_mapper(OldUser, self.users_table)
        except ArgumentError:
            pass # if SQLAlchemy doesn't like old-style classes
        else: # otherwise, they should work as well
            test_user = OldUser(user_id=2, user_name='Devine', password='Ned')
            assert test_user.user_id == 2
            assert test_user.user_name == 'Devine'
            assert test_user.password == 'Ned'

    def test_custom_contructor(self):
        """Mapped objects can also have their own constructors."""
        session_mapper(SecretUser, self.users_table)
        test_user = SecretUser(user_id=3, user_name='Falken')
        assert test_user.user_id == 3
        assert test_user.user_name == 'falken'
        assert test_user.password == 'secret'

    def test_no_contructor(self):
        """Mapped objects can also have no constructor at all."""
        session_mapper(RawUser, self.users_table, set_kwargs_on_init=False)
        self.assertRaises(TypeError, RawUser,
            user_id=4, user_name='Jonny', password='Walker')

    def test_no_validate(self):
        """Constructor of mapped objects does not validate kw args."""
        session_mapper(User, self.users_table)
        test_user = User(user_id=4, user_name='Falken', nickname='Steve')
        assert test_user.nickname == 'Steve'

    def test_validate(self):
        """Constructor of mapped objects can validate kw args."""
        session_mapper(User, self.users_table, validate=True)
        self.assertRaises(TypeError, User,
            user_id=4, user_name='Falken', nickname='Steve')

    def test_autoadd(self):
        """Mapped objects are automatically added to session."""
        session_mapper(User, self.users_table)
        test_user = User(user_id=5, user_name='Disney', password='Walt')
        assert test_user in session

    def test_no_autoadd(self):
        """Mapped objects can not be automatically added to session."""
        session_mapper(User, self.users_table, autoadd=False)
        test_user = User(user_id=6, user_name='Barks', password='Carl')
        assert test_user not in session
