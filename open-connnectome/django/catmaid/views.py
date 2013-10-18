import django.http
from django.views.decorators.cache import cache_control
import cStringIO

import empaths
import ocpcatmaid
import mcfccatmaid

# Errors we are going to catch
from emcaerror import EMCAError

import logging
logger=logging.getLogger("emca")



# Create your views here.

def ocpcatmaidview (request, webargs):
  """Convert a CATMAID request into an cutout."""

  try:
    oc = ocpcatmaid.OCPCatmaid()
    imgfobj = oc.getTile(webargs)
    return django.http.HttpResponse(imgfobj.read(), mimetype="image/png")

  except EMCAError, e:
    return django.http.HttpResponseNotFound(e)
  except Exception, e:
    logger.exception("Unknown exception in ocpcatmaidview: %s" % e )
    raise


# multi-channel false color
def mcfccatmaidview (request, webargs):
  """Convert a CATMAID request into an cutout."""

  try:
    mc = mcfccatmaid.MCFCCatmaid()
    imgfobj = mc.getTile(webargs)
    return django.http.HttpResponse(imgfobj.read(), mimetype="image/png")

  except EMCAError, e:
    return django.http.HttpResponseNotFound(e)
  except Exception, e:
    logger.exception("Unknown exception in mcfccatmaidview: %s" % e )
    raise

