from datetime import datetime

from sqlalchemy import Table, Column, String, DateTime
from sqlalchemy.orm import class_mapper, mapper
try:
    from sqlalchemy.orm.exc import UnmappedClassError
except ImportError: # SQLAlchemy < 0.5
    from sqlalchemy.exceptions import InvalidRequestError as UnmappedClassError

from turbogears import config
from turbogears.database import bind_metadata, metadata, session
from turbogears.util import load_class
from turbogears.visit.api import BaseVisitManager, Visit

import logging
log = logging.getLogger('turbogears.identity.savisit')

visit_class = None


class SqlAlchemyVisitManager(BaseVisitManager):

    def __init__(self, timeout):
        global visit_class
        visit_class_path = config.get('visit.saprovider.model',
            'turbogears.visit.savisit.TG_Visit')
        visit_class = load_class(visit_class_path)
        if visit_class is None:
            msg = 'No visit class found for %s' % visit_class_path
            msg += ', did you run setup.py develop?'
            log.error(msg)
        else:
            log.info("Successfully loaded '%s'", visit_class_path)
        if visit_class is TG_Visit:
            try:
                class_mapper(visit_class)
            except UnmappedClassError:
                visit_class._map()
        # base-class' __init__ triggers self.create_model,
        # so mappers need to be initialized before.
        super(SqlAlchemyVisitManager, self).__init__(timeout)

    def create_model(self):
        """Create the Visit table if it doesn't already exist."""
        bind_metadata()
        class_mapper(visit_class).local_table.create(checkfirst=True)
        log.debug("Visit model database table(s) created.")

    def new_visit_with_key(self, visit_key):
        """Return a new Visit object with the given key."""
        created = datetime.now()
        visit = visit_class()
        visit.visit_key = visit_key
        visit.created = created
        visit.expiry = created + self.timeout
        session.add(visit)
        session.flush()
        return Visit(visit_key, True)

    def visit_for_key(self, visit_key):
        """Return the visit (tg api Visit) for this key.

        Returns None if the visit doesn't exist or has expired.

        """
        try:
            expiry = self.queue[visit_key]
        except KeyError:
            visit = visit_class.lookup_visit(visit_key)
            if not visit:
                return None
            expiry = visit.expiry
        now = datetime.now(expiry.tzinfo)
        if expiry < now:
            return None
        # Visit hasn't expired, extend it
        self.update_visit(visit_key, now + self.timeout)
        return Visit(visit_key, False)

    def update_queued_visits(self, queue):
        # TODO this should be made transactional
        table = class_mapper(visit_class).mapped_table
        engine = table.bind
        # Now update each of the visits with the most recent expiry
        for visit_key, expiry in queue.items():
            log.info("updating visit (%s) to expire at %s", visit_key, expiry)
            engine.execute(table.update(table.c.visit_key == visit_key,
                values=dict(expiry=expiry)))


# The default Visit model class

class TG_Visit(object):

    @classmethod
    def lookup_visit(cls, visit_key):
        return session.query(cls).get(visit_key)

    @classmethod
    def _map(cls):
        cls._table = Table('visit', metadata,
            Column('visit_key', String(40), primary_key=True),
            Column('created', DateTime, nullable=False, default=datetime.now),
            Column('expiry', DateTime))
        cls._mapper = mapper(cls, cls._table)
