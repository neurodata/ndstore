import django.http

import numpy as np
from PIL import Image
import urllib2
import zlib

import cStringIO

import ocpcaproj
import ocpcarest

# Errors we are going to catch
from ocpcaerror import OCPCAError

from django.conf import settings

import logging
logger=logging.getLogger("ocp")

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
  #
  #  dev server and production server urls.
  #
  annourl = request.build_absolute_uri( '%s/ocpca/%s/%s' % ( request.META.get('SCRIPT_NAME'), token, cutout ))
#  annourl = request.build_absolute_uri( '/ocpca/%s/%s' % ( token, cutout ))

  # Get data 
  try:
    f = urllib2.urlopen ( dataurl )
    # create the data image
    fobj = cStringIO.StringIO ( f.read() )
    dataimg = Image.open(fobj) 

  except:
    logger.error("Failed to fetch dataurl {}".format(dataurl))
    raise


  # Get annotations 
  try:
    f = urllib2.urlopen ( annourl )
    # create the annotation image
    fobj = cStringIO.StringIO ( f.read() )
    annoimg = Image.open(fobj) 

  except:
    logger.error("Failed to fetch annourl {}".format(annourl))
    raise

  try:
    # convert data image to RGBA
    dataimg = dataimg.convert("RGBA")

    # build the overlay
    compimg = Image.composite ( annoimg, dataimg, annoimg )

    logger.warning("What up here.  {} {} {}".format(dataimg, annoimg, compimg))

  except Exception, e:
    logger.error ("Unknown error processing overlay images. Error={}".format(e))
    raise


  # Create blended image of the two
  return compimg


def imgAnnoOverlay (request, webargs):
  """Return overlayCutout as a png"""

  try:
     overlayimg = overlayCutout ( request, webargs )
  except Exception, e:
     raise
#    return django.http.HttpResponseNotFound(e)

  # write the merged image to a buffer
  fobj2 = cStringIO.StringIO ( )
  overlayimg.save ( fobj2, "PNG" )

  fobj2.seek(0)

  return django.http.HttpResponse(fobj2.read(), mimetype="image/png" )


