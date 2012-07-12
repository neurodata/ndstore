from django.http import HttpResponse, HttpRequest

import empaths
import zindex
import annrest

def index(request):
    return HttpResponse("This view works.")

def annoget (request, webargs):
  """Restful URL for all read services to annotation projects"""

# mimetype mg/png downloads the file.  image/png inlines the file.
  [ token , sym, cutoutargs ] = webargs.partition ('/')
  [ service, sym, rest ] = cutoutargs.partition ('/')

  if service=='xy' or service=='yz' or service=='xz':
    return HttpResponse(annrest.annoget(webargs), mimetype="image/png" )
  elif service=='hdf5':
    return HttpResponse(annrest.annoget(webargs), mimetype="product/hdf5" )
  elif service=='npz':
    return HttpResponse(annrest.annoget(webargs), mimetype="product/npz" )
  elif service=='xyanno':
    return HttpResponse(annrest.annoget(webargs), mimetype="image/png" )
  elif service=='id':
    return HttpResponse(annrest.annoget(webargs))
  else:
    return HttpResponseBadRequest ("Could not find service %s" % dataset )

def annopost (request, webargs):
  """Restful URL for all write/post services to annotation projects"""

  # All handling done by annrest
  return HttpResponse(annrest.annopost(webargs,request.body))

def annotation (request, webargs):
  """Get put object interface for RAMON objects"""

  if request.method == 'GET':
    return HttpResponse(annrest.getAnnotation(webargs), mimetype="product/hdf5" )
  elif request.method == 'POST':
    return HttpResponse(annrest.putAnnotation(webargs,request.body))

def post_test ( request ):
  return HttpResponse("<html> Post test </html>")

