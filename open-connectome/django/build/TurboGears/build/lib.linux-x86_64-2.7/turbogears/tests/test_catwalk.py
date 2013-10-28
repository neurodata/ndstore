import unittest

try:
    import json
except ImportError: # Python < 2.6
    import simplejson as json

from turbogears import controllers, expose, testutil
from turbogears.toolbox.catwalk import CatWalk

from catwalk_models import browse


#verbose run nosetests -s -v -f test_catwalk.py
#run nosetests -v -f test_catwalk.py


def setup_module():
    testutil.start_server()


def teardown_module():
    testutil.stop_server()


def browse_data(model):
    """load some test data, only once"""
    if model.Artist.select().count() > 0:
        return # only load once
    genres = '''Latin Jazz Rock Pop Metal Dance Hall
        Reggae Disco Funk Ska Swing Acid Folk Reggaeton
        World Classic Hip-Hop Rythm&Blues Blues'''.split()
    for genre in genres:
        model.Genre(name=genre)
    instruments = 'bass drum'.split()
    for instrument in instruments:
        model.Instrument(name=instrument)
    for artist_id in range(15):
        artist = model.Artist(name='Artist #%s'% artist_id)
        for album_id in range(15):
            album = model.Album(name='Album #%s_%s' % (
                artist_id, album_id), artist=artist)
            for song_id in range(15):
                model.Song(name='Song #%s_%s_%s' % (
                    artist_id, album_id, song_id), album=album)
        for genre in model.Genre.select():
            genre.addArtist(artist)


class MyRoot(controllers.RootController):

    @expose()
    def index(self):
        pass


class Browse(unittest.TestCase):

    def setUp(self):
        browse_data(browse)
        testutil.mount(MyRoot(), '/')
        testutil.mount(CatWalk(browse), '/catwalk')
        self.app = testutil.make_app()

    def test_wrong_filter_format(self):
        response = self.app.get('/catwalk/browse/'
            '?object_name=Song&filters=Guantanemera&tg_format=json')
        assert 'filter_format_error' in response

    def test_wrong_filter_column(self):
        response = self.app.get('/catwalk/browse/'
            '?object_name=Song&filters=guacamole:2&tg_format=json')
        assert 'filter_column_error' in response

    def test_filters(self):
        response = self.app.get('/catwalk/browse/'
            '?object_name=Song&tg_format=json')
        values = json.loads(response.body)
        # without the filters we get all songs (3375)
        assert values['total'] == 15 * 15 * 15
        response = self.app.get('/catwalk/browse/'
            '?object_name=Song&filters=album:1&tg_format=json')
        # values = json.loads(response.body)
        response.headers['Content-Type'] = 'application/json'
        values = response.json
        # filter by album id (only 15 songs)
        assert values['total'] == 15

    def test_response_fields(self):
        #Check that the response contains the expected keys
        response = self.app.get('/catwalk/browse/'
            '?object_name=Artist&start=3&page_size=20&tg_format=json')
        values = json.loads(response.body)
        assert 'headers' in values
        assert 'rows' in values
        assert 'start' in values
        assert 'page_size' in values
        assert 'total' in values
        assert values['start'] == 3
        assert values['page_size'] == 20
        assert values['total'] == 15

    def test_rows_joins_count(self):
        # Control that the count for related and multiple joins match
        # the number of related instances when accessed as a field
        response = self.app.get('/catwalk/browse/'
            '?object_name=Artist&tg_format=json')
        values = json.loads(response.body)
        artist = browse.Artist.get(1)
        assert int(values['rows'][0]['genres']) == len(list(artist.genres))
        assert int(values['rows'][0]['albums']) == len(list(artist.albums))

    def test_rows_column_number(self):
        # Control that the number of columns match
        # the number of fields in the model
        response = self.app.get('/catwalk/browse/'
            '?object_name=Artist&tg_format=json')
        values = json.loads(response.body)
        assert len(values['rows'][0]) == 4

    def test_rows_limit(self):
        # Update the limit of rows for the query
        # and control the number of rows returned
        response = self.app.get('/catwalk/browse/'
            '?object_name=Artist&tg_format=json')
        values = json.loads(response.body)
        assert 'rows' in values
        assert len(values['rows']) == 10
        response = self.app.get('/catwalk/browse/'
            '?object_name=Artist&page_size=15&tg_format=json')
        values = json.loads(response.body)
        assert 'rows' in values
        assert len(values['rows']) == 15

    def test_header_labels(self):
        # Check that the returned header labels match the the model
        response = self.app.get('/catwalk/browse/'
            '?object_name=Artist&tg_format=json')
        values = json.loads(response.body)
        assert len(values['headers']) == 5
        for header in values['headers']:
            assert header['name'] in (
                'id','name','albums','genres', 'plays_instruments')


class TestJoinedOperations(testutil.DBTest):

    model = browse

    def setUp(self):
        testutil.mount(MyRoot(), '/')
        testutil.mount(CatWalk(browse), '/catwalk')
        testutil.DBTest.setUp(self)
        browse_data(browse)
        self.app = testutil.make_app()

    def tearDown(self):
        testutil.DBTest.tearDown(self)

    def test_addremove_related_joins(self):
        # check the update_join function when nondefault add/remove are used
        artist = self.model.Artist.get(1)
        assert len(artist.plays_instruments) == 0
        self.app.get('/catwalk/updateJoins'
            '?objectName=Artist&id=1&join=plays_instruments&joinType='
            '&joinObjectName=Instrument&joins=1%2C2&tg_format=json')
        assert len(artist.plays_instruments) == 2
        self.app.get('/catwalk/updateJoins'
            '?objectName=Artist&id=1&join=plays_instruments&joinType='
            '&joinObjectName=Instrument&joins=1&tg_format=json')
        assert len(artist.plays_instruments) == 1

