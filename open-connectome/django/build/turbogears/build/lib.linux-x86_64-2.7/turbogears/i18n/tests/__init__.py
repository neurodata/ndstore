# i18n.tests

import os.path
from warnings import simplefilter, resetwarnings

from turbogears import config
from turbogears.i18n import sogettext


def setup_package():
    # DeprecationWarnings are ignored in Python 2.7 by default,
    # so add a filter that always shows them during the tests.
    simplefilter('always', DeprecationWarning)


def teardown_package():
    resetwarnings()


def setup_module():
    """Setup method that can be used by modules in this package."""
    basedir = os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))), 'tests')
    locale_dir = os.path.join(basedir, 'locale')
    config.update({
        'i18n.locale_dir': locale_dir,
        'i18n.domain': 'messages',
        'i18n.default_locale': 'en',
        'i18n.get_locale': lambda: 'en',
        'i18n.run_template_filter': False,
        'sqlobject.dburi': 'sqlite:///:memory:'
    })
    sogettext.create_so_catalog(['en', 'fi'], 'messages')
