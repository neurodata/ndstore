import django.http

import numpy as np
from PIL import Image
import urllib2
import zlib

import cStringIO

import ocpcaproj
import ocpcarest


"""Merge two cutouts one from a data set and one from an annotation database"""

def overlayCutout (request, webargs):
  """Get both data and annotation cubes as npz"""

  token, cutout = webargs.split('/',1)

  # Get the project and dataset
  projdb = ocpcaproj.OCPCAProjectsDB()
  proj = projdb.loadProject ( token )

  dataurl = request.build_absolute_uri( '%s/ocpca/%s/%s' % ( proj.getDataURL(), proj.getDataset(), cutout ))

  # RBTODO can't seen to get WSGIScriptAlias information from apache.  So 
  #  right now we have to hardwire.  Yuck.
  annourl = request.build_absolute_uri( '/ocpca/%s/%s' % ( token, cutout ))

  # Get data 
  f = urllib2.urlopen ( dataurl )

  fobj = cStringIO.StringIO ( f.read() )
  dataimg = Image.open(fobj) 

  # Get annotations 
  f = urllib2.urlopen ( annourl )

  fobj = cStringIO.StringIO ( f.read() )
  annoimg = Image.open(fobj) 


  # convert data image to RGBA
  dataimg = dataimg.convert("RGBA")

  # Create blended image of the two
  return Image.composite ( annoimg, dataimg, annoimg )


def imgAnnoOverlay (request, webargs):
  """Return overlayCutout as a png"""

  import pdb; pdb.set_trace()
  try:
     overlayimg = overlayCutout ( request, webargs )
  except Exception, e:
    return django.http.HttpResponseNotFound(e)

  # write the merged image to a buffer
  fobj2 = cStringIO.StringIO ( )
  overlayimg.save ( fobj2, "PNG" )

  fobj2.seek(0)

  return django.http.HttpResponse(fobj2.read(), mimetype="image/png" )


