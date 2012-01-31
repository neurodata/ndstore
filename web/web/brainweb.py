#!/usr/bin/env /usr/local/epd-7.0-2-rh5-x86_64/bin/python
import empaths
import web
import restargs
import brainrest
import annrest

web.config.debug=True

urls = (
  '/bock11/(.*)', 'bock11',
  '/hayworth5nm/(.*)', 'hayworth5nm',
  '/hayworth5nm.annotate/(.*)', 'hayworth5nmAnnotate',
  '/kasthuri11/(.*)', 'kasthuri11',
  )

app = web.application(urls, globals(), True)

class bock11:
  def GET(self,name):
    return brainrest.bock11(web.websafe(name))

class hayworth5nm:
  def GET(self,name):
    return brainrest.hayworth5nm(web.websafe(name))

class hayworth5nmAnnotate:
  def GET(self,name):
    return annrest.hayworth5nm(web.websafe(name))
  def POST(self,name):
    return annrest.hayworth5nmPost(web.websafe(name))

class kasthuri11:
  def GET(self,name):
    return brainrest.kasthuri11(web.websafe(name))

if __name__ == "__main__":
    app.run()

