import django.http

import numpy as np
from PIL import Image
import urllib2
import zlib

import cStringIO

# CATMAID parameter
CM_TILESIZE=256

"""Merge two cutouts one from a data set and one from an annotation database"""

def imgAnnoOverlay (request, webargs):
  """Get both data and annotation cubes as npz"""

  datatoken, annotoken, cutout = webargs.split('/',2)

#  dataurl = request.build_absolute_uri( '/emca/%s/%s' % ( datatoken, cutout ))
#  annourl = request.build_absolute_uri( '/emca/%s/%s' % ( annotoken, cutout ))

  # RBTODO can't seen to get WSGIScriptAlias information from apache.  So 
  #  right now we have to hardwire.  Yuck.
  dataurl = request.build_absolute_uri( '/EM/emca/%s/%s' % ( datatoken, cutout ))
  annourl = request.build_absolute_uri( '/EM/emca/%s/%s' % ( annotoken, cutout ))

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


def catmaid (request, webargs):
  """Convert a CATMAID request into an imgAnnoOverlay.
    Webargs are going to be in the form of project/res/xtile/ytile/ztile/"""

  project, resstr, xtilestr, ytilestr, zslicestr, rest = webargs.split('/',6)
  xtile = int(xtilestr)
  ytile = int(ytilestr)

  # Look up the project
  #  RBTODO for now.  Hard code the kasthuri11 and kat11
  if project == 'kat11':
    newwebargs = '%s/%s/xy/%s/%s,%s/%s,%s/%s/' % ( 'kasthuri11', 'kat11', resstr, xtile*CM_TILESIZE, (xtile+1)*CM_TILESIZE, ytile*CM_TILESIZE, (ytile+1)*CM_TILESIZE, zslicestr )

    return imgAnnoOverlay ( request, newwebargs )
     
  else:
    return django.http.HttpResponseNotFound("No such CATMAID project")



