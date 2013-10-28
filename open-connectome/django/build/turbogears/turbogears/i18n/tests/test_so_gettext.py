
import turbogears
from turbogears.i18n.tests import setup_module as basic_setup_module

from turbogears.i18n.tests.test_tg_gettext import test_gettext, test_ngettext
from turbogears.i18n.tests.test_tg_gettext import test_invalid_domain
from turbogears.i18n.tests.test_kidutils import test_match_template, test_i18n_filter

def setup_module():
    turbogears.config.update({'i18n.gettext': 'so_gettext'})
    basic_setup_module()

def teardown_module():
    turbogears.config.update({'i18n.gettext': 'tg_gettext'})

def test_so_gettext():
    test_gettext()
    test_ngettext()
    test_match_template()
    test_i18n_filter()
    test_invalid_domain()

