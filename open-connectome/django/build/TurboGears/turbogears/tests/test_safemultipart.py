"""Tests the SafeMultipartFilter for handling dodgy multipart requests."""

try:
    from cherrypy.lib import safemime
except ImportError: # CherryPy >= 3.2
    safemime = None
from webtest import TestRequest

from turbogears import config, controllers, expose
from turbogears.testutil import TGTest


class TestRoot(controllers.RootController):

    @expose()
    def flashupload(self, filedata, upload, filename):
        return dict(
            filedata=filedata.file.read(),
            filename=filename,
            upload=upload)


class SafeMultipartToolTest(TGTest):

    root = TestRoot

    config = {'server.max_request_body_size': 0}

    def setUp(self):
        super(SafeMultipartToolTest, self).setUp()
        if safemime: # CherryPy < 3.2 (not needed any more in newer versions)
            safemime.init()
            self.config.update(
                {'/flashupload': {'tools.safe_multipart.on': True}})
        config.update(self.config)

    def test_flash_upload(self):
        """File uploads from Flash clients work using the safe_multipart tool.

        Note that we have to set server.max_request_body_size = 0 for this test
        because otherwise the SizeCheckWrapper will mess with our input.
        Unfortunately, there is no way to deactivate the WebTest InputWrapper.
        And actually, the problem will only be revealed when running the
        CherryPy HTTP server, so we should really have a functional test here.

        """
        filedata = (
            '<?xml version="1.0" encoding="UTF-8"?>\r\n'
            '<projectDescription>\r\n'
            '</projectDescription>\r\n')
        body = (
            '------------KM7Ij5cH2KM7Ef1gL6ae0ae0cH2gL6\r\n'
            'Content-Disposition: form-data; name="filename"\r\n'
            '\r\n'
            '.project\r\n'
            '------------KM7Ij5cH2KM7Ef1gL6ae0ae0cH2gL6\r\n'
            'Content-Disposition: form-data; '
                'name="filedata"; filename=".project"\r\n'
            'Content-Type: application/octet-stream\r\n'
            '\r\n'
            + filedata +
            '\r\n'
            '------------KM7Ij5cH2KM7Ef1gL6ae0ae0cH2gL6\r\n'
            'Content-Disposition: form-data; name="upload"\r\n'
            '\r\n'
            'Submit Query\r\n'
            # Flash apps omit the trailing \r\n on the last line:
            '------------KM7Ij5cH2KM7Ef1gL6ae0ae0cH2gL6--')
        headers = [
            ('Accept', 'text/*'),
            ('Content-Type', 'multipart/form-data; '
                 'boundary=----------KM7Ij5cH2KM7Ef1gL6ae0ae0cH2gL6'),
            ('User-Agent', 'Shockwave Flash'),
            ('Host', 'www.example.com:8080'),
            ('Content-Length', str(len(body))),
            ('Connection', 'Keep-Alive'),
            ('Cache-Control', 'no-cache')]
        environ = self.app._make_environ(dict(REQUEST_METHOD='POST'))
        req = TestRequest.blank('/flashupload', environ)
        req.headers.update(dict(headers))
        req.body = body
        response = self.app.do_request(req, 200, True)
        assert response.raw['upload'] == 'Submit Query'
        assert response.raw['filename'] == '.project'
        assert response.raw['filedata'] == filedata
