# widgets.tests

from warnings import simplefilter, resetwarnings


def setup_package():
    # DeprecationWarnings are ignored in Python 2.7 by default,
    # so add a filter that always shows them during the tests.
    simplefilter('always', DeprecationWarning)


def teardown_package():
    resetwarnings()
