from sqlobject import *

__connection__ = connectionForURI('sqlite:///:memory:')
hub = __connection__

class Genre(SQLObject):
    name = StringCol()
    artists = RelatedJoin('Artist')

class Artist(SQLObject):
    name = StringCol()
    genres = RelatedJoin('Genre')
    albums = MultipleJoin('Album')

    plays_instruments = RelatedJoin('Instrument', addRemoveName='anInstrument',
                                    joinColumn='artist_id',
                                    otherColumn='plays_instrument_id',
                                    intermediateTable='artist_plays_instrument')
class Album(SQLObject):
    name = StringCol()
    artist = ForeignKey('Artist')
    songs = MultipleJoin('Song')

class Instrument(SQLObject):
    name = StringCol()
    played_by = RelatedJoin( 'Artist', joinColumn='artist_id',
                             otherColumn='plays_instrument_id',
                             intermediateTable='artist_plays_instrument')

class Song(SQLObject):
    name = StringCol()
    album = ForeignKey('Album')

Genre.createTable(ifNotExists=True)
Artist.createTable(ifNotExists=True)
Album.createTable(ifNotExists=True)
Song.createTable(ifNotExists=True)
Instrument.createTable(ifNotExists=True)
