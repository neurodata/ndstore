#!/usr/bin/env /use/local/epd-7.0-2-rh5-x86_64/bin/python
import web
import brainrest

web.config.debug=False

urls = (
  '/npz/(.*)', 'NumpyZip' ,
  '/hdf5/(.*)', 'HDF5' ,
  '/xy/(.*)', 'xy' ,
  '/xz/(.*)', 'xz' ,
  '/yz/(.*)', 'yz' )

app = web.application(urls, globals(), True)

class NumpyZip:
  def GET(self,name):
    return brainrest.numpyZip(web.websafe(name))

class HDF5:
  def GET(self,name):
    return brainrest.HDF5(web.websafe(name))

class xy:
  def GET(self,name):
    return brainrest.xyImage(web.websafe(name))

class xz:
  def GET(self,name):
    return brainrest.xzImage(web.websafe(name))

class yz:
  def GET(self,name):
    return brainrest.yzImage(web.websafe(name))

if __name__ == "__main__":
    app.run()

