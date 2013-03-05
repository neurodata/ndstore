import django.http
from django.views.decorators.cache import cache_control

import empaths
import catmaid

# Errors we are going to catch
from emcaerror import ANNError

import logging
logger=logging.getLogger("emca")



# Create your views here.

def catmaid (request, webargs):
  """Convert a CATMAID request into an cutout."""

  try:
    catmaidimg = emcarest.emcacatmaid(webargs)

    fobj = cStringIO.StringIO ( )
    catmaidimg.save ( fobj, "PNG" )
    fobj.seek(0)
    return django.http.HttpResponse(fobj.read(), mimetype="image/png")

  except ANNError, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in annopost.")
    raise
