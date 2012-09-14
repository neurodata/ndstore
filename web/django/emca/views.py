import django.http
import MySQLdb
import cStringIO

import empaths
import zindex
import emcarest
import emcaproj
import dbconfig

# Errors we are going to catch
from emcaerror import ANNError

def index(request):
    return django.http.HttpResponse("This view works.")

def emcaget (request, webargs):
  """Restful URL for all read services to annotation projects"""

  [ token , sym, cutoutargs ] = webargs.partition ('/')
  [ service, sym, rest ] = cutoutargs.partition ('/')

  try:
    if service=='xy' or service=='yz' or service=='xz':
      return django.http.HttpResponse(emcarest.emcaget(webargs), mimetype="image/png" )
    elif service=='hdf5':
      return django.http.HttpResponse(emcarest.emcaget(webargs), mimetype="product/hdf5" )
    elif service=='npz':
      return django.http.HttpResponse(emcarest.emcaget(webargs), mimetype="product/npz" )
    elif service=='xyanno' or service=='yzanno' or service=='xzanno':
      return django.http.HttpResponse(emcarest.emcaget(webargs), mimetype="image/png" )
    elif service=='id':
      return django.http.HttpResponse(emcarest.emcaget(webargs))
    elif service=='ids':
      return django.http.HttpResponse(emcarest.emcaget(webargs))
    else:
      return django.http.HttpResponseBadRequest ("Could not find service %s" % dataset )
  except (ANNError,MySQLdb.Error), e:
    return django.http.HttpResponseNotFound(e.value)


def annopost (request, webargs):
  """Restful URL for all write/post services to annotation projects"""

  # All handling done by emcarest
  try:
    return django.http.HttpResponse(emcarest.annopost(webargs,request.body))
  except ANNError, e:
    return django.http.HttpResponseNotFound(e.value)

def annotation (request, webargs):
  """Get put object interface for RAMON objects"""

  try:
    if request.method == 'GET':
      return django.http.HttpResponse(emcarest.getAnnotation(webargs), mimetype="product/hdf5" )
    elif request.method == 'POST':
      return django.http.HttpResponse(emcarest.putAnnotation(webargs,request.body))
    elif request.method == 'DELETE':
      emcarest.deleteAnnotation(webargs)
      return django.http.HttpResponse ("Success", mimetype='text/html')
  except ANNError, e:
    if hasattr(e,'value'):
      return django.http.HttpResponseNotFound(e.value)
    else: 
      return django.http.HttpResponseNotFound(e)
      
def getObjects ( request, webargs ):
  """Batch fetch of RAMON objects"""

  try:
    if request.method == 'GET':
      raise ANNError ( "GET requested. objects Web service requires a POST of a list of identifiers.")
    elif request.method == 'POST':
      return django.http.HttpResponse(emcarest.getAnnotations(webargs,request.body), mimetype="product/hdf5") 
    
  except ANNError, e:
    return django.http.HttpResponseNotFound(e.value)

def listObjects ( request, webargs ):
  """Return a list of objects matching predicates and cutout"""

  try:
    if request.method == 'GET':
      return django.http.HttpResponse(emcarest.listAnnoObjects(webargs), mimetype="product/hdf5") 
    elif request.method == 'POST':
      return django.http.HttpResponse(emcarest.listAnnoObjects(webargs,request.body), mimetype="product/hdf5") 
    
  except ANNError, e:
    return django.http.HttpResponseNotFound(e.value)


def catmaid (request, webargs):
  """Convert a CATMAID request into an cutout."""

  try:
    catmaidimg = emcarest.emcacatmaid(webargs)

    fobj = cStringIO.StringIO ( )
    catmaidimg.save ( fobj, "PNG" )
    fobj.seek(0)
    return django.http.HttpResponse(fobj.read(), mimetype="image/png")

  except Exception, e:
    return django.http.HttpResponseNotFound(e)



def projinfo (request, webargs):
  """Return project and dataset configuration information"""

  return django.http.HttpResponse(emcarest.projInfo(webargs), mimetype="product/hdf5" )
