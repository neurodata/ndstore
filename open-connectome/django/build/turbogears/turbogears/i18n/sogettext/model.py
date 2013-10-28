from datetime import datetime

from sqlobject import (SQLObject, ForeignKey, MultipleJoin,
    DateTimeCol, StringCol, UnicodeCol)

from turbogears.database import PackageHub


hub = PackageHub('turbogears.i18n.sogettext')
__connection__ = hub


class TG_Domain(SQLObject):

    class sqlmeta:
        table = 'tg_i18n_domain'
        defaultOrder = 'name'

    name = StringCol(alternateID=True)
    messages = MultipleJoin('TG_Message')


class TG_Message(SQLObject):

    class sqlmeta:
        table = 'tg_i18n_message'
        defaultOrder = 'name'

    name = UnicodeCol()
    text = UnicodeCol(default='')
    domain = ForeignKey('TG_Domain')
    locale = StringCol(length=15)
    created = DateTimeCol(default=datetime.now)
    updated = DateTimeCol(default=None)

    def _set_text(self, text):

        self._SO_set_text(text)
        self.updated = datetime.now()

