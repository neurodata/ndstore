import django.http

import empaths
import zindex
import annrest

# Errors we are going to catch
from annerror import ANNError
import MySQLdb

def index(request):
    return django.http.HttpResponse("This view works.")

def annoget (request, webargs):
  """Restful URL for all read services to annotation projects"""

  [ token , sym, cutoutargs ] = webargs.partition ('/')
  [ service, sym, rest ] = cutoutargs.partition ('/')

  try:
    if service=='xy' or service=='yz' or service=='xz':
      return django.http.HttpResponse(annrest.annoget(webargs), mimetype="image/png" )
    elif service=='hdf5':
      return django.http.HttpResponse(annrest.annoget(webargs), mimetype="product/hdf5" )
    elif service=='npz':
      return django.http.HttpResponse(annrest.annoget(webargs), mimetype="product/npz" )
    elif service=='xyanno' or service=='yzanno' or service=='xzanno':
      return django.http.HttpResponse(annrest.annoget(webargs), mimetype="image/png" )
    elif service=='id':
      return django.http.HttpResponse(annrest.annoget(webargs))
    elif service=='listids':
      return django.http.HttpResponse(annrest.annoget(webargs))
    else:
      return django.http.HttpResponseBadRequest ("Could not find service %s" % dataset )
  except (ANNError,MySQLdb.Error), e:
    return django.http.HttpResponseNotFound(e.value)


def annopost (request, webargs):
  """Restful URL for all write/post services to annotation projects"""

  # All handling done by annrest
  try:
    return django.http.HttpResponse(annrest.annopost(webargs,request.body))
  except ANNError, e:
    return django.http.HttpResponseNotFound(e.value)

def annotation (request, webargs):
  """Get put object interface for RAMON objects"""

  try:
    if request.method == 'GET':
      return django.http.HttpResponse(annrest.getAnnotation(webargs), mimetype="product/hdf5" )
    elif request.method == 'POST':
      return django.http.HttpResponse(annrest.putAnnotation(webargs,request.body))
  except ANNError, e:
    if hasattr(e,'value'):
      return django.http.HttpResponseNotFound(e.value)
    else: 
      return django.http.HttpResponseNotFound(e)
      

def getannoids ( request, webargs ):

  try:
    if request.method == 'GET':
      return django.http.HttpResponse(annrest.getAnnoIDs(webargs), mimetype="product/hdf5") 
    elif request.method == 'POST':
      return django.http.HttpResponse(annrest.getAnnoIDs(webargs,request.body), mimetype="product/hdf5") 
    
  except ANNError, e:
    return django.http.HttpResponseNotFound(e.value)

