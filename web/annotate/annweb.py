#!/usr/bin/env /usr/local/epd-7.0-2-rh5-x86_64/bin/python
import web
import annrest

web.config.debug=True

# RBTODO factor out the services into a common file.

urls = (
  '/bock11/(.*)', 'bock11' ,
  '/hayworth5nm/(.*)', 'hayworth5nm' ,
  '/kasthuri11/(.*)', 'kasthuri11' )

app = web.application(urls, globals(), True)

class bock11:
  def GET(self,name):
    return annrest.bock11(web.websafe(name))

class hayworth5nm:
  def GET(self,name):
    return annrest.hayworth5nm(web.websafe(name))

class kasthuri11:
  def GET(self,name):
    return annrest.kasthuri11(web.websafe(name))

if __name__ == "__main__":
    app.run()

