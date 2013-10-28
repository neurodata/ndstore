# identity.tests

from warnings import filterwarnings, simplefilter, resetwarnings


def setup_package():
    # Ignore warning about deprecation of cgi.parse_qs from CherryPy 3.1.2
    filterwarnings('ignore', r'cgi\.parse_qs', PendingDeprecationWarning, 'cherrypy')
    # DeprecationWarnings are ignored in Python 2.7 by default,
    # so add a filter that always shows them during the tests.
    simplefilter('always', DeprecationWarning)


def teardown_package():
    resetwarnings()
