import django.http

import numpy as np
from PIL import Image
import urllib2
import zlib

import cStringIO

#TODO need to get url from django

"""Merge two cutouts one from a data set and one from an annotation database"""


def overlay (request, webargs):
  """Get both data and annotation cubes as npz"""

  import pdb; pdb.set_trace()

  # Build the urls for the two requests
  if request.is_secure():
    protocol = "https"
  else:
    protocol = "http"

  baseurl=request.get_host()

  datatoken, annotoken, cutout = webargs.split('/',2)

  dataurl = '%s://%s/emca/%s/%s' % ( protocol, baseurl, datatoken, cutout )
  annourl = '%s://%s/emca/%s/%s' % ( protocol, baseurl, annotoken, cutout )

  # Get data 
  try:
    f = urllib2.urlopen ( dataurl )
  except urllib2.URLError, e:
    return django.http.HttpResponseNotFound(e)

  fobj = cStringIO.StringIO ( f.read() )
  dataimg = Image.open(fobj) 

  # Get annotations 
  try:
    f = urllib2.urlopen ( annourl )
  except urllib2.URLError, e:
    return django.http.HttpResponseNotFound(e)

  fobj = cStringIO.StringIO ( f.read() )
  annoimg = Image.open(fobj) 

  # convert data image to RGBA
  dataimg = dataimg.convert("RGBA")

  # build a mask out of the annoimg
  annodata = np.asarray ( annoimg )

  # Create blended image of the two
  compimg = Image.composite ( annoimg, dataimg, annoimg )

  # write the merged image to a buffer
  fobj2 = cStringIO.StringIO ( )
  compimg.save ( fobj2, "PNG" )

  fobj2.seek(0)
  return django.http.HttpResponse(fobj2.read(), mimetype="image/png" )



