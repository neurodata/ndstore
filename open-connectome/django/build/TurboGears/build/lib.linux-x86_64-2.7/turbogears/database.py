"""Convenient access to an SQLObject or SQLAlchemy managed database."""

__all__ = ['AutoConnectHub', 'bind_metadata', 'create_session',
    'create_session_mapper', 'commit_all', 'end_all',
    'DatabaseError', 'DatabaseConfigurationError',
    'EndTransactions', 'get_engine', 'get_metadata', 'mapper',
    'metadata', 'PackageHub', 'rollback_all', 'session',
    'session_mapper', 'set_db_uri', 'so_columns', 'so_joins', 'so_to_dict']

import sys
import time
import logging

import cherrypy
from cherrypy import request

try:
    import sqlalchemy, sqlalchemy.orm
    from sqlalchemy import MetaData
    try:
        from sqlalchemy.exc import ArgumentError, OperationalError
    except ImportError: # SQLAlchemy < 0.5
        from sqlalchemy.exceptions import ArgumentError, OperationalError
except ImportError:
    sqlalchemy = None

try:
    import sqlobject
    from sqlobject.dbconnection import ConnectionHub, Transaction, TheURIOpener
    from sqlobject.util.threadinglocal import local as threading_local
except ImportError:
    sqlobject = None

from peak.rules import abstract, when, NoApplicableMethods

from turbogears import config
from turbogears.util import remove_keys

log = logging.getLogger('turbogears.database')


class DatabaseError(Exception):
    """TurboGears Database Error."""


class DatabaseConfigurationError(DatabaseError):
    """TurboGears Database Configuration Error."""


# Provide support for SQLAlchemy
if sqlalchemy:

    def get_engine(pkg=None):
        """Retrieve the engine based on the current configuration."""
        bind_metadata()
        return get_metadata(pkg).bind

    def get_metadata(pkg=None):
        """Retrieve the metadata for the specified package."""
        try:
            return _metadatas[pkg]
        except KeyError:
            _metadatas[pkg] = MetaData()
            return _metadatas[pkg]

    def bind_metadata():
        """Connect SQLAlchemy to the configured database(s)."""
        if metadata.is_bound():
            return

        alch_args = dict()
        for k, v in config.items():
            if 'sqlalchemy' in k:
                alch_args[k.split('.', 1)[-1]] = v

        try:
            dburi = alch_args.pop('dburi')
            if not dburi:
                raise KeyError
            metadata.bind = sqlalchemy.create_engine(dburi, **alch_args)
        except KeyError:
            raise DatabaseConfigurationError(
                "No sqlalchemy database configuration found!")
        except ArgumentError, exc:
            raise DatabaseConfigurationError(exc)

        global _using_sa
        _using_sa = True

        for k, v in config.items():
            if '.dburi' in k and 'sqlalchemy.' not in k:
                get_metadata(k.split('.', 1)[0]
                    ).bind = sqlalchemy.create_engine(v, **alch_args)

    def create_session():
        """Create a session that uses the engine from thread-local metadata.

        The session by default does not begin a transaction, and requires that
        flush() be called explicitly in order to persist results to the database.

        """
        if not metadata.is_bound():
            bind_metadata()
        return sqlalchemy.orm.create_session()

    session = sqlalchemy.orm.scoped_session(create_session)

    if not hasattr(session, 'add'): # SQLAlchemy < 0.5
        session.add = session.save_or_update

    # Note: TurboGears used to set mapper = Session.mapper, but this has
    # been deprecated in SQLAlchemy 0.5.5. If it is unavailable, we emulate
    # the behaviour of the old session-aware mapper following this recipe
    # from the SQLAlchemy wiki:
    #
    # http://www.sqlalchemy.org/trac/wiki/UsageRecipes/SessionAwareMapper
    #
    # If you do not want to use the session-aware mapper, import 'mapper'
    # directly from sqlalchemy.orm. See model.py in the default quickstart
    # template for an example.
    def create_session_mapper(scoped_session=session):
        def mapper(cls, *args, **kw):
            set_kwargs_on_init = kw.pop('set_kwargs_on_init', True)
            validate = kw.pop('validate', False)
            # we accept 'save_on_init' as an alias for 'autoadd' for backward
            # compatibility, but 'autoadd' is shorter and more to the point.
            autoadd = kw.pop('autoadd', kw.pop('save_on_init', True))

            if set_kwargs_on_init and (getattr(cls,
                        '__init__', object.__init__) is object.__init__
                    or getattr(cls.__init__, '_session_mapper', False)):
                def __init__(self, **kwargs):
                    for key, value in kwargs.items():
                        if validate:
                            if not hasattr(self, key):
                                raise TypeError(
                                    "Invalid __init__ argument: '%s'" % key)
                        setattr(self, key, value)
                    if autoadd:
                        session.add(self)
                __init__._session_mapper = True
                cls.__init__ = __init__
            cls.query = scoped_session.query_property()
            return sqlalchemy.orm.mapper(cls, *args, **kw)
        return mapper
    session_mapper = create_session_mapper()
    if hasattr(session, 'mapper'):
        # Old session-aware mapper
        mapper = session.mapper
    else:
        mapper = session_mapper

    _metadatas = {}
    _metadatas[None] = MetaData()
    metadata = _metadatas[None]

    try:
        import elixir
        elixir.metadata, elixir.session = metadata, session
    except ImportError:
        pass

else:
    def get_engine():
        pass
    def get_metadata():
        pass
    def bind_metadata():
        pass
    def create_session():
        pass
    session = metadata = mapper = None

bind_meta_data = bind_metadata # deprecated, for backward compatibility

hub_registry = set()

_hubs = dict() # stores the AutoConnectHubs used for each connection URI

# Provide support for SQLObject
if sqlobject:
    def _mysql_timestamp_converter(raw):
        """Timestamp-converter for MySQL.

        Convert a MySQL TIMESTAMP to a floating point number representing
        the seconds since the Un*x Epoch. It uses custom code the input seems
        to be the new (MySQL 4.1+) timestamp format, otherwise code from the
        MySQLdb module is used.

        """
        if raw[4] == '-':
            return time.mktime(time.strptime(raw, '%Y-%m-%d %H:%M:%S'))
        else:
            import MySQLdb.converters
            return MySQLdb.converters.mysql_timestamp_converter(raw)


    class AutoConnectHub(ConnectionHub):
        """Connect to the database once per thread.

        The AutoConnectHub also provides convenient methods for managing
        transactions.

        """
        uri = None
        params = {}

        def __init__(self, uri=None, supports_transactions=True):
            if not uri:
                uri = config.get('sqlobject.dburi')
            self.uri = uri
            self.supports_transactions = supports_transactions
            hub_registry.add(self)
            ConnectionHub.__init__(self)

        def _is_interesting_version(self):
            """Return True only if version of MySQLdb <= 1.0."""
            import MySQLdb
            module_version = MySQLdb.version_info[0:2]
            major = module_version[0]
            minor = module_version[1]
            # we can't use Decimal here because it is only available for Python 2.4
            return major < 1 or (major == 1 and minor < 2)

        def _enable_timestamp_workaround(self, connection):
            """Enable timestamp-workaround for MySQL.

            Enable a workaround for an incompatible timestamp format change
            in MySQL 4.1 when using an old version of MySQLdb. See trac ticket
            #1235 - http://trac.turbogears.org/ticket/1235 for details.

            """
            # precondition: connection is a MySQLConnection
            import MySQLdb
            import MySQLdb.converters
            if self._is_interesting_version():
                conversions = MySQLdb.converters.conversions.copy()
                conversions[MySQLdb.constants.FIELD_TYPE.TIMESTAMP] = \
                    _mysql_timestamp_converter
                # There is no method to use custom keywords when using
                # "connectionForURI" in SQLObject so we have to insert the
                # conversions afterwards.
                connection.kw['conv'] = conversions

        def getConnection(self):
            try:
                conn = self.threadingLocal.connection
                return self.begin(conn)
            except AttributeError:
                uri = self.uri
                if uri:
                    conn = sqlobject.connectionForURI(uri)
                    # the following line effectively turns off the DBAPI connection
                    # cache. We're already holding on to a connection per thread,
                    # and the cache causes problems with SQLite.
                    if uri.startswith('sqlite'):
                        TheURIOpener.cachedURIs = {}
                    elif uri.startswith('mysql') and config.get('turbogears.'
                            'enable_mysql41_timestamp_workaround', False):
                        self._enable_timestamp_workaround(conn)
                    self.threadingLocal.connection = conn
                    return self.begin(conn)
                raise AttributeError("No connection has been defined"
                    " for this thread or process")

        def reset(self):
            """Used for testing purposes.

            This drops all of the connections that are being held.

            """
            self.threadingLocal = threading_local()

        def begin(self, conn=None):
            """Start a transaction."""
            if not self.supports_transactions:
                return conn
            if not conn:
                conn = self.getConnection()
            if isinstance(conn, Transaction):
                if conn._obsolete:
                    conn.begin()
                return conn
            self.threadingLocal.old_conn = conn
            trans = conn.transaction()
            self.threadingLocal.connection = trans
            return trans

        def commit(self):
            """Commit the current transaction."""
            if not self.supports_transactions:
                return
            try:
                conn = self.threadingLocal.connection
            except AttributeError:
                return
            if isinstance(conn, Transaction):
                self.threadingLocal.connection.commit()

        def rollback(self):
            """Rollback the current transaction."""
            if not self.supports_transactions:
                return
            try:
                conn = self.threadingLocal.connection
            except AttributeError:
                return
            if isinstance(conn, Transaction) and not conn._obsolete:
                self.threadingLocal.connection.rollback()

        def end(self):
            """End the transaction, returning to a standard connection."""
            if not self.supports_transactions:
                return
            try:
                conn = self.threadingLocal.connection
            except AttributeError:
                return
            if not isinstance(conn, Transaction):
                return
            if not conn._obsolete:
                conn.rollback()
            self.threadingLocal.connection = self.threadingLocal.old_conn
            del self.threadingLocal.old_conn
            self.threadingLocal.connection.expireAll()

    class PackageHub(object):
        """A package specific database hub.

        Transparently proxies to an AutoConnectHub for the URI
        that is appropriate for this package. A package URI is
        configured via "packagename.dburi" in the TurboGears config
        settings. If there is no package DB URI configured, the
        default (provided by "sqlobject.dburi") is used.

        The hub is not instantiated until an attempt is made to
        use the database.

        """
        def __init__(self, packagename):
            self.packagename = packagename
            self.hub = None

        def __get__(self, obj, type):
            if self.hub:
                return self.hub.__get__(obj, type)
            else:
                return self

        def __set__(self, obj, type):
            if not self.hub:
                self.set_hub()
            return self.hub.__set__(obj, type)

        def __getattr__(self, name):
            if not self.hub:
                self.set_hub()
            try:
                return getattr(self.hub, name)
            except AttributeError:
                return getattr(self.hub.getConnection(), name)

        def set_hub(self):
            dburi = config.get('%s.dburi' % self.packagename, None)
            if not dburi:
                dburi = config.get('sqlobject.dburi', None)
            if not dburi:
                raise DatabaseConfigurationError(
                    "No sqlobject database configuration found!")
            if dburi.startswith('notrans_'):
                dburi = dburi[8:]
                trans = False
            else:
                trans = True
            hub = _hubs.get(dburi, None)
            if not hub:
                hub = AutoConnectHub(dburi, supports_transactions=trans)
                _hubs[dburi] = hub
            self.hub = hub
else:
    class AutoConnectHub(object):
        pass

    class PackageHub(object):
        pass


def set_db_uri(dburi, package=None):
    """Set the database URI.

    Sets the database URI to use either globally or for a specific package.
    Note that once the database is accessed, calling it will have no effect.

    @param dburi: database URI to use
    @param package: package name this applies to, or None to set the default.

    """
    if package:
        config.update({'%s.dburi' % package: dburi})
    else:
        config.update({'sqlobject.dburi': dburi})


def commit_all():
    """Commit the transactions in all registered hubs (for this thread)."""
    for hub in hub_registry:
        hub.commit()


def rollback_all():
    """Rollback the transactions in all registered hubs (for this thread)."""
    for hub in hub_registry:
        hub.rollback()


def end_all():
    """End the transactions in all registered hubs (for this thread)."""
    for hub in hub_registry:
        hub.end()


@abstract()
def run_with_transaction(func, *args, **kw):
    pass


@abstract()
def restart_transaction(args):
    pass


_using_sa = False

def _use_sa(args=None):
    return _using_sa


# include "args" to avoid call being pre-cached
@when(run_with_transaction, "not _use_sa(args)")
def so_rwt(func, *args, **kw):
    log.debug("Starting SQLObject transaction")
    try:
        try:
            retval = func(*args, **kw)
            commit_all()
            return retval
        except cherrypy.HTTPRedirect:
            commit_all()
            raise
        except cherrypy.InternalRedirect:
            commit_all()
            raise
        except:
            # No need to "rollback" the sqlalchemy unit of work,
            # because nothing has hit the db yet.
            rollback_all()
            raise
    finally:
        end_all()


# include "args" to avoid call being pre-cached
@when(restart_transaction, "not _use_sa(args)")
def so_restart_transaction(args):
    # log.debug("ReStarting SQLObject transaction")
    # Disable for now for compatibility
    pass


def dispatch_exception(exception, args, kw):
    # errorhandling import here to avoid circular imports
    from turbogears.errorhandling import dispatch_error
    # Keep in mind func is not the real func but _expose
    real_func, accept, allow_json, controller = args[:4]
    args = args[4:]
    exc_type, exc_value, exc_trace = sys.exc_info()
    remove_keys(kw, ('tg_source', 'tg_errors', 'tg_exceptions'))
    try:
        output = dispatch_error(
            controller, real_func, None, exception, *args, **kw)
    except NoApplicableMethods:
        raise exc_type, exc_value, exc_trace
    else:
        del exc_trace
        return output


# include "args" to avoid call being pre-cached
@when(run_with_transaction, "_use_sa(args)")
def sa_rwt(func, *args, **kw):
    log.debug("Starting SA transaction")
    request.sa_transaction = session.begin()
    try:
        try:
            retval = func(*args, **kw)
        except (cherrypy.HTTPRedirect, cherrypy.InternalRedirect):
            # If a redirect happens, commit and proceed with redirect.
            if sa_transaction_active():
                log.debug('Redirect in active transaction - will commit now')
                session.commit()
            else:
                log.debug('Redirect in inactive transaction')
            raise
        except:
            # If any other exception happens, rollback and re-raise error
            if sa_transaction_active():
                log.debug('Error in active transaction - will rollback now')
                session.rollback()
            else:
                log.debug('Error in inactive transaction')
            raise
        # If the call was successful, commit and proceed
        if sa_transaction_active():
            log.debug('Transaction is still active - will commit now')
            session.commit()
        else:
            log.debug('Transaction is already inactive')
    finally:
        log.debug('Ending SA transaction')
        session.close()
    return retval


# include "args" to avoid call being pre-cached
@when(restart_transaction, "_use_sa(args)")
def sa_restart_transaction(args):
    log.debug("Restarting SA transaction")
    if sa_transaction_active():
        log.debug('Transaction is still active - will rollback now')
        session.rollback()
    else:
        log.debug('Transaction is already inactive')
    session.close()
    request.sa_transaction = session.begin()


def sa_transaction_active():
    """Check whether SA transaction is still active."""
    try:
        return session.is_active
    except AttributeError: # SA < 0.4.9
        try:
            return session().is_active
        except (TypeError, AttributeError): # SA < 0.4.7
            try:
                transaction = request.sa_transaction
                return transaction and transaction.is_active
            except AttributeError:
                return False


def so_to_dict(sqlobj):
    """Convert SQLObject to a dictionary based on columns."""
    d = {}
    if sqlobj is None:
        return d # stops recursion
    for name in sqlobj.sqlmeta.columns.keys():
        d[name] = getattr(sqlobj, name)
    d['id'] = sqlobj.id # id must be added explicitly
    if sqlobj._inheritable:
        d.update(so_to_dict(sqlobj._parent))
        d.pop('childName')
    return d


def so_columns(sqlclass, columns=None):
    """Return a dict with all columns from a SQLObject.

    This includes the columns from InheritableSO's bases.

    """
    if columns is None:
        columns = {}
    columns.update(filter(lambda i: i[0] != 'childName',
                          sqlclass.sqlmeta.columns.items()))
    if sqlclass._inheritable:
        so_columns(sqlclass.__base__, columns)
    return columns


def so_joins(sqlclass, joins=None):
    """Return a list with all joins from a SQLObject.

    The list includes the columns from InheritableSO's bases.

    """
    if joins is None:
        joins = []
    joins.extend(sqlclass.sqlmeta.joins)
    if sqlclass._inheritable:
        so_joins(sqlclass.__base__, joins)
    return joins


def EndTransactions():
    if _use_sa():
        try:
            session.expunge_all()
        except AttributeError: # SQLAlchemy < 0.5.1
            session.clear()
    else:
        end_all()

