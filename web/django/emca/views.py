import django.http
from django.views.decorators.cache import cache_control
import MySQLdb
import cStringIO

import empaths
import zindex
import emcarest
import emcaproj

# Errors we are going to catch
from emcaerror import EMCAError

import logging
logger=logging.getLogger("emca")


def getCutout (request, webargs):
  """Restful URL for all read services to annotation projects"""

  [ token , sym, cutoutargs ] = webargs.partition ('/')
  [ service, sym, rest ] = cutoutargs.partition ('/')

  try:
    if service=='xy' or service=='yz' or service=='xz':
      return django.http.HttpResponse(emcarest.getCutout(webargs), mimetype="image/png" )
    elif service=='hdf5':
      return django.http.HttpResponse(emcarest.getCutout(webargs), mimetype="product/hdf5" )
    elif service=='npz':
      return django.http.HttpResponse(emcarest.getCutout(webargs), mimetype="product/npz" )
    elif service=='zip':
      return django.http.HttpResponse(emcarest.getCutout(webargs), mimetype="product/zip" )
    elif service=='xyanno' or service=='yzanno' or service=='xzanno':
      return django.http.HttpResponse(emcarest.getCutout(webargs), mimetype="image/png" )
    elif service=='id':
      return django.http.HttpResponse(emcarest.getCutout(webargs))
    elif service=='ids':
      return django.http.HttpResponse(emcarest.getCutout(webargs))
    else:
      logger.warning ("HTTP Bad request. Could not find service %s" % service )
      return django.http.HttpResponseBadRequest ("Could not find service %s" % service )
  except EMCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in getCutout.")
    raise


@cache_control(no_cache=True)
def annopost (request, webargs):
  """Restful URL for all write/post services to annotation projects"""
  import pdb;pdb.set_trace()
  # All handling done by emcarest
  try:
    return django.http.HttpResponse(emcarest.annopost(webargs,request.body))
  except EMCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in annopost.")
    raise

@cache_control(no_cache=True)
def annotation (request, webargs):
  """Get put object interface for RAMON objects"""
  import pdb;pdb.set_trace()
  try:
    if request.method == 'GET':
      return django.http.HttpResponse(emcarest.getAnnotation(webargs), mimetype="product/hdf5" )
    elif request.method == 'POST':
      import pdb;pdb.set_trace()
      return django.http.HttpResponse(emcarest.putAnnotation(webargs,request.body))
    elif request.method == 'DELETE':
      emcarest.deleteAnnotation(webargs)
      return django.http.HttpResponse ("Success", mimetype='text/html')
  except EMCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in annotation.")
    raise


@cache_control(no_cache=True)
def csv (request, webargs):
  """Get (not yet put) csv interface for RAMON objects"""

  try:
    if request.method == 'GET':
      return django.http.HttpResponse(emcarest.getCSV(webargs), mimetype="text/html" )
  except EMCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in csv.")
    raise
      
@cache_control(no_cache=True)
def getObjects ( request, webargs ):
  """Batch fetch of RAMON objects"""

  try:
    if request.method == 'GET':
      raise EMCAError ( "GET requested. objects Web service requires a POST of a list of identifiers.")
    elif request.method == 'POST':
      return django.http.HttpResponse(emcarest.getAnnotations(webargs,request.body), mimetype="product/hdf5") 
    
  except EMCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in getObjects.")
    raise

@cache_control(no_cache=True)
def queryObjects ( request, webargs ):
  """Return a list of objects matching predicates and cutout"""

  try:
    if request.method == 'GET':
      return django.http.HttpResponse(emcarest.queryAnnoObjects(webargs), mimetype="product/hdf5") 
    elif request.method == 'POST':
      return django.http.HttpResponse(emcarest.queryAnnoObjects(webargs,request.body), mimetype="product/hdf5") 
    
  except EMCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in listObjects.")
    raise


def catmaid (request, webargs):
  """Convert a CATMAID request into an cutout."""

  try:
    catmaidimg = emcarest.emcacatmaid_legacy(webargs)

    fobj = cStringIO.StringIO ( )
    catmaidimg.save ( fobj, "PNG" )
    fobj.seek(0)
    return django.http.HttpResponse(fobj.read(), mimetype="image/png")

  except EMCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in catmaid %s.", e)
    raise


def projinfo (request, webargs):
  """Return project and dataset configuration information"""
  
  try:  
    return django.http.HttpResponse(emcarest.projInfo(webargs), mimetype="product/hdf5" )
  except EMCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in projInfo.")
    raise


def chaninfo (request, webargs):
  """Return channel information"""

  try:  
    return django.http.HttpResponse(emcarest.chanInfo(webargs), mimetype="text/html" )
  except EMCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in chanInfo.")
    raise


def mcFalseColor (request, webargs):
  """Cutout of multiple channels with false color rendering"""

  try:
    return django.http.HttpResponse(emcarest.mcFalseColor(webargs), mimetype="image/png" )
  except EMCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in mcFalseColor.")
    raise


def setField (request, webargs):
  """Set an individual RAMON field for an object"""

  try:
    emcarest.setField(webargs)
    return django.http.HttpResponse()
  except EMCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in setField.")
    raise


def getField (request, webargs):
  """Get an individual RAMON field for an object"""

  try:
    return django.http.HttpResponse(emcarest.getField(webargs), mimetype="text/html" )
  except EMCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in getField.")
    raise

def merge (request, webargs):
  """Merge annotation objects"""

  try:
    return django.http.HttpResponse(emcarest.merge(webargs), mimetype="text/html" )
  except EMCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in global Merge.")
    raise
