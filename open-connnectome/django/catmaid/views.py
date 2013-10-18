import django.http
from django.views.decorators.cache import cache_control
import cStringIO

import prefetchcatmaid
import mcfccatmaid
import simplecatmaid

# Errors we are going to catch
from ocpcaerror import OCPCAError

import logging
logger=logging.getLogger("ocp")



# Create your views here.

def prefetchcatmaidview (request, webargs):
  """Convert a CATMAID request into an cutout."""

  try:
    pfc = prefetchcatmaid.PrefetchCatmaid()
    imgfobj = pfc.getTile(webargs)
    return django.http.HttpResponse(imgfobj.read(), mimetype="image/png")

  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e)
  except Exception, e:
    logger.exception("Unknown exception in catmaidview: %s" % e )
    raise


# multi-channel false color
def mcfccatmaidview (request, webargs):
  """Convert a CATMAID request into an cutout."""

  try:
    mc = mcfccatmaid.MCFCCatmaid()
    imgfobj = mc.getTile(webargs)
    return django.http.HttpResponse(imgfobj.read(), mimetype="image/png")

  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e)
  except Exception, e:
    logger.exception("Unknown exception in mcfccatmaidview: %s" % e )
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

