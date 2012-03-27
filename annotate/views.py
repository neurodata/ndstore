from django.http import HttpResponse

import empaths
import zindex
import annrest

def index(request):
    return HttpResponse("This view works.")

def annoget (request, webargs):
  """Restful URL for all read services to annotation projects"""

  import pdb; pdb.set_trace()

# mimetype mg/png downloads the file.  image/png inlines the file.
  [ token , sym, cutoutargs ] = webargs.partition ('/')
  [ service, sym, rest ] = cutoutargs.partition ('/')

  if service=='xy' or service=='yz' or service=='xz':
    return HttpResponse(annrest.annoget(webargs), mimetype="image/png" )
  elif service=='hdf5':
    return HttpResponse(annrest.annoget(webargs), mimetype="product/hdf5" )
  elif service=='npz':
    return HttpResponse(annrest.annoget(webargs), mimetype="produc/npz" )
  else:
    return HttpResponseBadRequest ("Could not find service %s" % dataset )

def post_test ( request ):
  return HttpResponse("<html> Post test </html>")

