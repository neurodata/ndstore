from datetime import datetime
from sqlalchemy import *
from sqlalchemy.orm import relation
from turbogears import database

database.set_db_uri('sqlite:///:memory:', 'sqlalchemy')
database.get_engine()
metadata = database.metadata
metadata.bind.echo = True

groups_table = Table('tg_group', metadata,
    Column('group_id', Integer, primary_key=True),
    Column('group_name', Unicode(16), unique=True),
    Column('display_name', Unicode(255)),
    Column('created', DateTime, default=datetime.now)
)

users_table = Table('tg_user', metadata,
    Column('user_id', Integer, primary_key=True),
    Column('user_name', Unicode(16), unique=True),
    Column('email_address', Unicode(255), unique=True),
    Column('display_name', Unicode(255)),
    Column('password', Unicode(40)),
    Column('created', DateTime, default=datetime.now)
)

user_group_table = Table('user_group', metadata,
    Column('user_id', Integer, ForeignKey('tg_user.user_id')),
    Column('group_id', Integer, ForeignKey('tg_group.group_id'))
)

class User(object):
    
    def __repr__(self):
        return "class User user_id=%s email_address=%s display_name=%s" % (
                self.user_id, self.email_address, self.display_name)
    
class Group(object):
    pass
    
gmapper = database.mapper(Group, groups_table)
umapper = database.mapper(User, users_table, properties=dict(
    groups = relation(Group, secondary=user_group_table, backref='users')
    )
)
