import django.http
from django.views.decorators.cache import cache_control
import cStringIO

import empaths
import catmaid

# Errors we are going to catch
from emcaerror import EMCAError

import logging
logger=logging.getLogger("emca")



# Create your views here.

def catmaidview (request, webargs):
  """Convert a CATMAID request into an cutout."""

  try:
    catmaidimg = catmaid.catmaid(webargs)

    fobj = cStringIO.StringIO ( )
    catmaidimg.save ( fobj, "PNG" )
    fobj.seek(0)
    return django.http.HttpResponse(fobj.read(), mimetype="image/png")

  except EMCAError, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in annopost.")
    raise
