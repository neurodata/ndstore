from sqlobject import *

__connection__ = connectionForURI("sqlite:///:memory:")
hub = __connection__

class Client(SQLObject):
    name = StringCol()
    physical_address=SingleJoin('Address')
    #shipping_address=SingleJoin('Address')

class Address(SQLObject):
    client=ForeignKey('Client',default=None)
    street=StringCol()

Client.createTable(ifNotExists=True)
Address.createTable(ifNotExists=True)
