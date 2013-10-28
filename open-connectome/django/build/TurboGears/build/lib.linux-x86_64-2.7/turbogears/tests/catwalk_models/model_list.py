from sqlobject import SQLObject, StringCol, connectionForURI

__connection__ = connectionForURI('sqlite:///:memory:')
hub = __connection__

class FirstClass(SQLObject):
    name = StringCol(title="This is a title", length=200, default="new name")

class SecondClass(SQLObject):
    name = StringCol()

class ThirdClass(SQLObject):
    name = StringCol()

FirstClass.createTable(ifNotExists=True)
SecondClass.createTable(ifNotExists=True)
ThirdClass.createTable(ifNotExists=True)
