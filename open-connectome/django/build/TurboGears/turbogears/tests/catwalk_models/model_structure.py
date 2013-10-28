from sqlobject import SQLObject, StringCol, IntCol, connectionForURI

__connection__ = connectionForURI('sqlite:///:memory:')
hub = __connection__

class StringTest(SQLObject):
    name = StringCol(title="This is a title", length=200, default='new name')
StringTest.createTable(ifNotExists=True)

class NumTest(SQLObject):
    an_integer = IntCol(title="This is an integer", default=123)
NumTest.createTable(ifNotExists=True)
