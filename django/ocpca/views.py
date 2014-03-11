import django.http
from django.views.decorators.cache import cache_control
import MySQLdb
import cStringIO

import zindex
import ocpcarest
import ocpcaproj

# Errors we are going to catch
from ocpcaerror import OCPCAError

import logging
logger=logging.getLogger("ocp")

def cutout (request, webargs):
  """Restful URL for all read services to annotation projects"""

  [ token , sym, cutoutargs ] = webargs.partition ('/')
  [ service, sym, rest ] = cutoutargs.partition ('/')

  try:
    # GET methods
    if request.method == 'GET':
      if service=='xy' or service=='yz' or service=='xz':
        return django.http.HttpResponse(ocpcarest.getCutout(webargs), mimetype="image/png" )
      elif service=='hdf5':
        return django.http.HttpResponse(ocpcarest.getCutout(webargs), mimetype="product/hdf5" )
      elif service=='npz':
        return django.http.HttpResponse(ocpcarest.getCutout(webargs), mimetype="product/npz" )
      elif service=='zip':
        return django.http.HttpResponse(ocpcarest.getCutout(webargs), mimetype="product/zip" )
      elif service=='xyanno' or service=='yzanno' or service=='xzanno':
        return django.http.HttpResponse(ocpcarest.getCutout(webargs), mimetype="image/png" )
      elif service=='id':
        return django.http.HttpResponse(ocpcarest.getCutout(webargs))
      elif service=='ids':
        return django.http.HttpResponse(ocpcarest.getCutout(webargs))
      else:
        logger.warning ("HTTP Bad request. Could not find service %s" % service )
        return django.http.HttpResponseBadRequest ("Could not find service %s" % service )

    # RBTODO control caching?
    # POST methods
    elif request.method == 'POST':
      if service=='hdf5' or service=='npz':
        django.http.HttpResponse(ocpcarest.putCutout(webargs,request.body))
        return django.http.HttpResponse ("Success", mimetype='text/html')
      else:
        logger.warning ("HTTP Bad request. Could not find service %s" % service )
        return django.http.HttpResponseBadRequest ("Could not find service %s" % service )

    else:
      logger.warning ("Invalid HTTP method %s.  Not GET or POST." % request.method )
      return django.http.HttpResponseBadRequest ("Invalid HTTP method %s.  Not GET or POST." % request.method )

  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in getCutout.")
    raise

@cache_control(no_cache=True)
def annotation (request, webargs):
  """Get put object interface for RAMON objects"""

  try:
    if request.method == 'GET':
      return django.http.HttpResponse(ocpcarest.getAnnotation(webargs), mimetype="product/hdf5" )
    elif request.method == 'POST':
      return django.http.HttpResponse(ocpcarest.putAnnotation(webargs,request.body))
    elif request.method == 'DELETE':
      ocpcarest.deleteAnnotation(webargs)
      return django.http.HttpResponse ("Success", mimetype='text/html')
  except OCPCAError, e:
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
      return django.http.HttpResponse(ocpcarest.getCSV(webargs), mimetype="text/html" )
  except OCPCAError, e:
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
      raise OCPCAError ( "GET requested. objects Web service requires a POST of a list of identifiers.")
    elif request.method == 'POST':
      return django.http.HttpResponse(ocpcarest.getAnnotations(webargs,request.body), mimetype="product/hdf5") 
    
  except OCPCAError, e:
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
      return django.http.HttpResponse(ocpcarest.queryAnnoObjects(webargs), mimetype="product/hdf5") 
    elif request.method == 'POST':
      return django.http.HttpResponse(ocpcarest.queryAnnoObjects(webargs,request.body), mimetype="product/hdf5") 
    
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in listObjects.")
    raise


def catmaid (request, webargs):
  """Convert a CATMAID request into an cutout."""

  try:
    catmaidimg = ocpcarest.ocpcacatmaid_legacy(webargs)

    fobj = cStringIO.StringIO ( )
    catmaidimg.save ( fobj, "PNG" )
    fobj.seek(0)
    return django.http.HttpResponse(fobj.read(), mimetype="image/png")

  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in catmaid %s.", e)
    raise


@cache_control(no_cache=True)
def publictokens (request, webargs):
  """Return list of public tokens"""
  try:  
    return django.http.HttpResponse(ocpcarest.publicTokens(webargs), mimetype="application/json" )
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in publictokens.")
    raise


@cache_control(no_cache=True)
def jsoninfo (request, webargs):
  """Return project and dataset configuration information"""

  try:  
    return django.http.HttpResponse(ocpcarest.jsonInfo(webargs), mimetype="application/json" )
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in jsoninfo.")
    raise

@cache_control(no_cache=True)
def projinfo (request, webargs):
  """Return project and dataset configuration information"""
  
  try:  
    return django.http.HttpResponse(ocpcarest.projInfo(webargs), mimetype="product/hdf5" )
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in projInfo.")
    raise


@cache_control(no_cache=True)
def chaninfo (request, webargs):
  """Return channel information"""

  try:  
    return django.http.HttpResponse(ocpcarest.chanInfo(webargs), mimetype="application/json" )
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in chanInfo.")
    raise


def mcFalseColor (request, webargs):
  """Cutout of multiple channels with false color rendering"""

  try:
    return django.http.HttpResponse(ocpcarest.mcFalseColor(webargs), mimetype="image/png" )
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in mcFalseColor.")
    raise


def setField (request, webargs):
  """Set an individual RAMON field for an object"""

  try:
    ocpcarest.setField(webargs)
    return django.http.HttpResponse()
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in setField.")
    raise


@cache_control(no_cache=True)
def getField (request, webargs):
  """Get an individual RAMON field for an object"""

  try:
    return django.http.HttpResponse(ocpcarest.getField(webargs), mimetype="text/html" )
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in getField.")
    raise

def merge (request, webargs):
  """Merge annotation objects"""

  try:
    return django.http.HttpResponse(ocpcarest.merge(webargs), mimetype="text/html" )
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in global Merge.")
    raise


def exceptions (request, webargs):
  """Return a list of multiply labeled pixels in a cutout region"""

  try:
    return django.http.HttpResponse(ocpcarest.exceptions(webargs), mimetype="product/hdf5" )
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in exceptions Web service.")
    raise

