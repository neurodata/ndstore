import django.http

import numpy as np
from PIL import Image
import urllib2
import zlib

import cStringIO

import empaths
import emcaproj

from emcaerror import ANNError

# CATMAID parameter
CM_TILESIZE=256

"""Merge two cutouts one from a data set and one from an annotation database"""

def overlayCutout (request, webargs):
  """Get both data and annotation cubes as npz"""

  datatoken, annotoken, cutout = webargs.split('/',2)

  dataurl = request.build_absolute_uri( '/emca/%s/%s' % ( datatoken, cutout ))
  annourl = request.build_absolute_uri( '/emca/%s/%s' % ( annotoken, cutout ))

  # RBTODO can't seen to get WSGIScriptAlias information from apache.  So 
  #  right now we have to hardwire.  Yuck.
#  dataurl = request.build_absolute_uri( '/EM/emca/%s/%s' % ( datatoken, cutout ))
#  annourl = request.build_absolute_uri( '/EM/emca/%s/%s' % ( annotoken, cutout ))

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

  # build a mask out of the annoimg
  annodata = np.asarray ( annoimg )

  # Create blended image of the two
  return Image.composite ( annoimg, dataimg, annoimg )


def imgAnnoOverlay (request, webargs):
  """Return overlayCutout as a png"""
  try:
     overlayimg = overlayCutout ( request, webargs )
  except Exception, e:
    return django.http.HttpResponseNotFound(e)

  # write the merged image to a buffer
  fobj2 = cStringIO.StringIO ( )
  overlayimg.save ( fobj2, "PNG" )

  fobj2.seek(0)

  return django.http.HttpResponse(fobj2.read(), mimetype="image/png" )

def catmaid (request, webargs):
  """Convert a CATMAID request into an imgAnnoOverlay.
    Webargs are going to be in the form of project/res/xtile/ytile/ztile/"""

  import pdb; pdb.set_trace()
#
  token, plane, resstr, xtilestr, ytilestr, zslicestr, rest = webargs.split('/',7)
  xtile = int(xtilestr)
  ytile = int(ytilestr)

  # Get the project and dataset
  try:
    projdb = emcaproj.EMCAProjectsDB()
    proj = projdb.getProj ( token )

    # build the overlay request
    if plane=='xy':

      newwebargs = '%s/%s/%s/%s/%s,%s/%s,%s/%s/' % ( proj.getDataset(), token, plane, resstr, xtile*CM_TILESIZE, (xtile+1)*CM_TILESIZE, ytile*CM_TILESIZE, (ytile+1)*CM_TILESIZE, zslicestr )

      overlayimg = overlayCutout ( request, newwebargs )

    else:
      raise ANNError ( "No such cutout plane: %s.  Must be (xy|xz|yz)." % plane )


  except Exception, e:
    return django.http.HttpResponseNotFound(e)

  # write the merged image to a buffer
  fobj2 = cStringIO.StringIO ( )
  overlayimg.save ( fobj2, "PNG" )

  fobj2.seek(0)

  return django.http.HttpResponse(fobj2.read(), mimetype="image/png" )
