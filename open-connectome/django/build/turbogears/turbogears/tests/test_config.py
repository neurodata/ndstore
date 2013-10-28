import logging
import ntpath
import os
import re
import sys

from cStringIO import StringIO

import pkg_resources
from turbogears import config, update_config

rfn = pkg_resources.resource_filename
testfile = rfn(__name__, 'configfile.cfg')

logout = StringIO()
logging.logout = logout
cget = config.get


def test_update_from_package():
    update_config(modulename='turbogears.tests.config')
    assert cget('foo.bar') == 'BAZ!'
    # last forward slash (the one before static) is hard coded in our config
    # file... all other path separators are calculated platform wise...
    assert cget('my.static').endswith(
        'turbogears%stests/static' % os.path.sep)
    assert config.app['/static']['tools.staticdir.on'] == False


def test_update_from_both():
    update_config(configfile = testfile, modulename='turbogears.tests.config')
    assert cget('foo.bar') == 'blurb'
    assert cget('tg.something') == 10
    assert cget('test.dir').endswith('turbogears%stests' % os.path.sep)
    assert cget('visit.cookie.path') == '/acme'
    assert cget('tools.visit.cookie.path') == '/acme'


callnum = 0

def windows_filename(*args, **kw):
    """Small helper function to emulate pkg_resources.resource_filename
    as if it was called on a Windows system even if the tester is in fact
    using Linux or Mac OS X.

    We need to keep track how often the function was called, since
    'turbogears.update_config' calls 'pkg_resources.resource_filename' at least
    twice and we only want to return the fake Windows path the second and
    following times.

    """
    global callnum
    callnum += 1
    if callnum > 1:
        return 'c:\\foo\\bar\\'
    else:
        return rfn(*args, **kw)


def test_update_on_windows():
    """turbogears.update_config works as we intend on Windows."""
    # save the original function
    orig_resource_fn = pkg_resources.resource_filename
    # monkey patch pkg resources to emulate windows
    pkg_resources.resource_filename = windows_filename

    update_config(configfile=testfile, modulename='turbogears.tests.config')
    testdir = cget('test.dir')
    # update_config calls os.normpath on package_dir, but this will have no
    # effect on non-windows systems, so we call ntpath.normpath on those here
    if not sys.platform.startswith('win'):
        testdir = ntpath.normpath(testdir)

    # restore original function
    pkg_resources.resource_filename = orig_resource_fn
    assert testdir == 'c:\\foo\\bar'


def test_logging_config():
    logout.truncate(0)
    log = logging.getLogger('turbogears.tests.test_config.logconfig')
    log.info("Testing")
    logged = logout.getvalue()
    assert re.match(r'F1 \d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d INFO '
        'Testing', logged)
