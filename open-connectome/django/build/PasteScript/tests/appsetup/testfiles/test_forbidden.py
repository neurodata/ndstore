from paste.fixture import *

def test_forbidden():
    # Unfortunately, auth isn't enabled in the standard app
    # yet, so we ignore that
    return
    app = TestApp() # Of what?
    app.get('/')
    #app.get('/admin/', status=401)
    #app.get('/admin/', status=403,
    #        extra_environ={'REMOTE_USER': 'bob'})
    
