"""Standard TurboGears request dispatchers for CherryPy."""

__all__ = ['VirtualPathDispatcher']

from cherrypy import NotFound, dispatch, request


class VirtualPathDispatcher(object):
    """Dispatcher that makes CherryPy ignorant of a URL root path.

    That is, you can mount your app so the URI "/users/~rdel/myapp/" maps to
    the root object "/".

    Note that this can not be done by a hook since they are run too late.

    """

    def __init__(self, next_dispatcher=None, webpath=''):
        self.next_dispatcher = next_dispatcher or dispatch.Dispatcher()
        webpath = webpath.strip('/')
        if webpath:
            webpath = '/' + webpath
        self.webpath = webpath

    def __call__(self, path_info):
        """Determine the relevant path info by stripping off prefixes.

        Strips webpath and request.script_name from request.path_info.

        """
        webpath = self.webpath
        try:
            webpath += request.script_name.rstrip('/')
        except AttributeError:
            pass
        if webpath:
            request.script_name = webpath
            if path_info.startswith(webpath + '/'):
                request.path_info = path_info = path_info[len(webpath):]
            else:
                # check for webpath only if not forwarded
                try:
                    if not request.prev and not request.wsgi_environ[
                            'HTTP_X_FORWARDED_SERVER']:
                        raise KeyError
                except (AttributeError, KeyError):
                    raise NotFound(path_info)
        return self.next_dispatcher(path_info)
