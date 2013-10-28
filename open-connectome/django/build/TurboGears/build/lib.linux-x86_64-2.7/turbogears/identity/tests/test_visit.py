# -*- coding: UTF-8 -*-

"""ORM independent Visit tests and test controllers."""

import cherrypy

from turbogears import config, controllers, expose, visit


def cookie_header(response):
    """Returns a dict containing cookie information to pass to a server."""
    return dict(Cookie=response.headers['Set-Cookie'])


class SimpleVisitPlugin(object):

    def record_request(self, visit):
        cherrypy.request.simple_visit_plugin = visit

    def register(self):
        visit.enable_visit_plugin(self)


class VisitRoot(controllers.RootController):

    @expose()
    def index(self):
        new = key = None
        cur_visit = visit.current()
        if cur_visit:
            new = cur_visit.is_new
            key = cur_visit.key
        visit_on = config.get('visit.on')
        return dict(new=new, key=key, visit_on=visit_on)

    @expose()
    def visit_plugin(self):
        vi = cherrypy.request.simple_visit_plugin
        return dict(key=vi.key, is_new=vi.is_new)

