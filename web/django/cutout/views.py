from django.http import HttpResponse

import empaths
import zindex
import brainrest

def index(request):
    return HttpResponse("This view works.")

#def hayworth5nm_png (request, webargs):
## mimetype mg/png downloads the file.  image/png inlines the file.
#    return HttpResponse(brainrest.hayworth5nm(webargs), mimetype="image/png" )

#def hayworth5nm_hdf5 (request, webargs):
#    return HttpResponse(brainrest.hayworth5nm(webargs), mimetype="product/hdf5" )

#def hayworth5nm_npz (request, webargs):
#    return HttpResponse(brainrest.hayworth5nm(webargs), mimetype="product/npz" )

# TODO get all the DB info into data models
#    and turn these into three calls on for png, one for hdf5 and one for npz

# Need some try/catch vodoo and turns all asserts into errors.

def cutout_png (request, webargs):
  """Restful URL for xy,yz,xz service to look at slices"""

# mimetype mg/png downloads the file.  image/png inlines the file.
  [ dataset , sym, cutoutargs ] = webargs.partition ('/')
  if dataset  == 'hayworth5nm':
    return HttpResponse(brainrest.hayworth5nm(cutoutargs), mimetype="image/png" )
  elif dataset  == 'bock11':
    return HttpResponse(brainrest.bock11(cutoutargs), mimetype="image/png" )
  elif dataset  == 'kasthuri11':
    return HttpResponse(brainrest.kasthuri11(cutoutargs), mimetype="image/png" )
  else:
    return HttpResponseBadRequest ("Could not find dataset %s" % dataset )

def cutout_hdf5 (request, webargs):
  """Restful URL for an HDF5 cutout"""
  [ dataset , sym, cutoutargs ] = webargs.partition ('/')
  if dataset  == 'hayworth5nm':
    return HttpResponse(brainrest.hayworth5nm(cutoutargs), mimetype="product/hdf5" )
  elif dataset  == 'bock11':
    return HttpResponse(brainrest.bock11(cutoutargs), mimetype="product/hdf5" )
  elif dataset  == 'kasthuri11':
    return HttpResponse(brainrest.kasthuri11(cutoutargs), mimetype="product/hdf5" )
  else: 
    return HttpResponseBadRequest ("Could not find dataset %s" % dataset )

def cutout_npz (request, webargs):
  """Restful URL for an numpy pickle that is zipped cutout"""
  [ dataset , sym, cutoutargs ] = webargs.partition ('/')
  if dataset  == 'hayworth5nm':
    return HttpResponse(brainrest.hayworth5nm(cutoutargs), mimetype="product/npz" )
  elif dataset  == 'bock11':
    return HttpResponse(brainrest.bock11(cutoutargs), mimetype="product/npz" )
  elif dataset  == 'kasthuri11':
    return HttpResponse(brainrest.kasthuri11(cutoutargs), mimetype="product/npz" )
  else:
    return HttpResponseBadRequest ("Could not find dataset %s" % dataset )

