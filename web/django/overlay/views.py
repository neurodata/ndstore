import django.http

import numpy as np
from PIL import Image
import urllib2
import zlib

import cStringIO

import empaths
import emcaproj
import emcarest
import dbconfig

from emcaerror import ANNError


"""Merge two cutouts one from a data set and one from an annotation database"""

def overlayCutout (request, webargs):
  """Get both data and annotation cubes as npz"""

  token, cutout = webargs.split('/',1)

  # Get the project and dataset
  projdb = emcaproj.EMCAProjectsDB()
  proj = projdb.getProj ( token )

  dataurl = request.build_absolute_uri( '%s/emca/%s/%s' % ( proj.getDataURL(), proj.getDataset(), cutout ))

  # RBTODO can't seen to get WSGIScriptAlias information from apache.  So 
  #  right now we have to hardwire.  Yuck.
  annourl = request.build_absolute_uri( '/emca/%s/%s' % ( token, cutout ))

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

  try:
     overlayimg = overlayCutout ( request, webargs )
  except Exception, e:
    return django.http.HttpResponseNotFound(e)

  # write the merged image to a buffer
  fobj2 = cStringIO.StringIO ( )
  overlayimg.save ( fobj2, "PNG" )

  fobj2.seek(0)

  return django.http.HttpResponse(fobj2.read(), mimetype="image/png" )


############### Run CATMAID through the cutout service

# CATMAID parameter
CM_TILESIZE=256

def catmaid (request, webargs):
  """Convert a CATMAID request into an imgAnnoOverlay.
    Webargs are going to be in the form of project/res/xtile/ytile/ztile/"""

  try:

    token, imageargs = webargs.split('/',1)

    # Get the project and dataset
    projdb = emcaproj.EMCAProjectsDB()
    proj = projdb.getProj ( token )

    annimg = emcarest.emcacatmaid(webargs)

    #  fetch data from url
    dataurl = request.build_absolute_uri( '%s/emca/catmaid/%s/%s' % ( proj.getDataURL(), proj.getDataset(), imageargs ))
    # Get data 
    f = urllib2.urlopen ( dataurl )
    fobj = cStringIO.StringIO ( f.read() )
    dataimg = Image.open(fobj) 

    # upsample the dataimage to 32 bit RGBA
    dataimg = dataimg.convert("RGBA")
    # make a composite of the two images
    compimg = Image.composite ( annimg, dataimg, annimg )

    # write the merged image to a buffer
    fobj2 = cStringIO.StringIO ( )
    compimg.save ( fobj2, "PNG" )

    fobj2.seek(0)

    return django.http.HttpResponse(fobj2.read(), mimetype="image/png" )

  except Exception, e:
    return django.http.HttpResponseNotFound(e)

