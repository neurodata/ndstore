import cherrypy

import turbogears
from turbogears import controllers
from turbogears import testutil

def setup_module():
    testutil.unmount()
    testutil.mount(MyRoot())
    testutil.start_server()

def teardown_module():
    testutil.unmount()
    testutil.stop_server()

class MyRoot(controllers.RootController):
    def set_name(self, name):
        cherrypy.response.cookie['name'] = name
        return "Hello " + name
    set_name = turbogears.expose()(set_name)

    def get_name(self):
        cookies = cherrypy.request.cookie
        if 'name' in cookies:
            return cookies['name'].value
        else:
            return "cookie not found"
    get_name = turbogears.expose()(get_name)

    def get_unicode_name(self):
        """Return a nonsense string of non-ascii characters"""
        cherrypy.response.headers['Content-Type'] = 'text/plain; encoding=utf-8'
        return u'\u1234\u9876\u3456'.encode('utf-8')
    get_unicode_name = turbogears.expose()(get_unicode_name)

def test_browser_session():
    bs = testutil.BrowsingSession()
    bs.goto('/get_name')
    assert bs.response == 'cookie not found'
    bs.goto('/set_name?name=me')
    assert bs.cookie['name'] == 'me'
    bs.goto('/get_name')
    assert bs.response == 'me'

def test_browser_session_for_two_users():
    bs1 = testutil.BrowsingSession()
    bs2 = testutil.BrowsingSession()
    bs1.goto('/set_name?name=bs1')
    bs2.goto('/set_name?name=bs2')
    bs1.goto('/get_name')
    assert bs1.response == 'bs1'
    bs2.goto('/get_name')
    assert bs2.response == 'bs2'

def test_unicode_response():
    bs = testutil.BrowsingSession()
    bs.goto('/get_unicode_name')
    assert bs.response == u'\u1234\u9876\u3456'.encode('utf-8')
    assert bs.unicode_response == u'\u1234\u9876\u3456'
    assert type(bs.unicode_response) == unicode
