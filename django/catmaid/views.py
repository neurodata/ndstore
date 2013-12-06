import django.http
from django.views.decorators.cache import cache_control
import cStringIO

import mcfccatmaid
import simplecatmaid
import colorcatmaid

# Errors we are going to catch
from ocpcaerror import OCPCAError

import logging
logger=logging.getLogger("ocp")


# multi-channel false color
def mcfccatmaidview (request, webargs):
  """multi-channel false color"""

  try:
    mc = mcfccatmaid.MCFCCatmaid()
    imgfobj = mc.getTile(webargs)
    return django.http.HttpResponse(imgfobj.read(), mimetype="image/png")

  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e)
  except Exception, e:
    logger.exception("Unknown exception in mcfccatmaidview: %s" % e )
    raise

# single-channel choose the color
def colorcatmaidview (request, webargs):
  """single-channel choose the color"""

  try:
    cc = colorcatmaid.ColorCatmaid()
    imgfobj = cc.getTile(webargs)
    return django.http.HttpResponse(imgfobj.read(), mimetype="image/png")

  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e)
  except Exception, e:
    logger.exception("Unknown exception in colorcatmaidview: %s" % e )
    raise

# simple per-tile interface
def simplecatmaidview (request, webargs):
  """Convert a CATMAID request into an cutout."""

  try:
    sc = simplecatmaid.SimpleCatmaid()
    imgfobj = sc.getTile(webargs)
    return django.http.HttpResponse(imgfobj.read(), mimetype="image/png")

  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e)
  except Exception, e:
    logger.exception("Unknown exception in simplecatmaidview: %s" % e )
    raise

