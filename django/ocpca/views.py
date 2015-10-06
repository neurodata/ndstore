# Copyright 2014 Open Connectome Project (http://openconnecto.me)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import django.http
from django.views.decorators.cache import cache_control
import MySQLdb
import cStringIO
import re

import ocpcarest
import jsonproj

from ocpcaerror import OCPCAError
import logging
logger=logging.getLogger("ocp")


GET_SLICE_SERVICES = ['xy', 'yz', 'xz']
GET_ANNO_SERVICES = ['xyanno', 'yzanno', 'xzanno']
POST_SERVICES = ['hdf5', 'npz', 'hdf5_async', 'propagate', 'tiff', 'blosc']


def cutout (request, webargs):
  """Restful URL for all read services to annotation projects"""
  
  try:
    m = re.match(r"(\w+)/(?P<channel>[\w+,/-]+)?/?(xy|xz|yz|tiff|hdf5|jpeg|blosc|npz|zip|id|ids|xyanno|xzanno|yzanno)/([\w,/-]+)$", webargs)
    [token, channel, service, cutoutargs] = [i for i in m.groups()]

    if channel is None:
      webargs = '{}/default/{}/{}'.format(token, service, cutoutargs)

  except Exception, e:
    logger.warning("Incorrect format for arguments {}. {}".format(webargs, e))
    raise OCPCAError("Incorrect format for arguments {}. {}".format(webargs, e))

  try:
    # GET methods
    if request.method == 'GET':
      if service in GET_SLICE_SERVICES+GET_ANNO_SERVICES:
        return django.http.HttpResponse(ocpcarest.getCutout(webargs), content_type="image/png" )
      elif service in ['hdf5']:
        fname = re.sub ( r',','_', webargs )
        fname = re.sub ( r'/','-', fname )
        response = django.http.HttpResponse(ocpcarest.getCutout(webargs), content_type="product/hdf5" )
        response['Content-Disposition'] = "attachment; filename={}ocpcutout.h5".format(fname)
        return response
      elif service in ['blosc']:
        fname = re.sub ( r',','_', webargs )
        fname = re.sub ( r'/','-', fname )
        response = django.http.HttpResponse(ocpcarest.getCutout(webargs), content_type="product/blosc" )
        response['Content-Disposition'] = "attachment; filename={}ocpcutout.blosc".format(fname)
        return response
      elif service in ['jpeg']:
        fname = re.sub ( r',','_', webargs )
        fname = re.sub ( r'/','-', fname )
        response = django.http.HttpResponse(ocpcarest.getCutout(webargs), content_type="product/jpeg" )
        response['Content-Disposition'] = "attachment; filename={}ocpcutout.jpeg".format(fname)
        return response
      elif service in ['npz']:
        return django.http.HttpResponse(ocpcarest.getCutout(webargs), content_type="product/npz" )
      elif service in ['tiff']:
        # build a file name from the webarguments
        fname = re.sub ( r',','_', webargs )
        fname = re.sub ( r'/','-', fname )
        response = django.http.HttpResponse(ocpcarest.getCutout(webargs), content_type="image/tiff" )
        response['Content-Disposition'] = "attachment; filename={}ocpcutout.tif".format(fname)
        return response
      elif service in ['zip']:
        return django.http.HttpResponse(ocpcarest.getCutout(webargs), content_type="product/zip" )
      elif service in ['id','ids']:
        return django.http.HttpResponse(ocpcarest.getCutout(webargs))
      else:
        logger.warning("HTTP Bad request. Could not find service {}".format(service))
        return django.http.HttpResponseBadRequest("Could not find service {}".format(service))

    # RBTODO control caching?
    # POST methods
    elif request.method == 'POST':
      if service in POST_SERVICES:
        django.http.HttpResponse(ocpcarest.putCutout(webargs, request.body))
        return django.http.HttpResponse("Success", content_type='text/html')
      else:
        logger.warning("HTTP Bad request. Could not find service {}".format(service))
        return django.http.HttpResponseBadRequest("Could not find service {}".format(service))

    else:
      logger.warning("Invalid HTTP method {}. Not GET or POST.".format(request.method))
      return django.http.HttpResponseBadRequest("Invalid HTTP method {}. Not GET or POST.".format(request.method))

  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except Exception, e:
    logger.exception("Unknown exception in getCutout.")
    raise OCPCAError("Unknown exception in getCutout")

#@cache_control(no_cache=True)
def nifti (request, webargs):
  """Get put interface for nifti files"""

  try:
    if request.method == 'GET':
      fname = "".join([x if x.isalnum() else "_" for x in webargs])
      response = django.http.HttpResponse(ocpcarest.getNIFTI(webargs), content_type="product/nii" )
      response['Content-Disposition'] = "attachment; filename={}.nii".format(fname)
      return response
    elif request.method == 'POST':
      return django.http.HttpResponse(ocpcarest.putNIFTI(webargs,request.body))
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in NIFTI.")
    raise


#@cache_control(no_cache=True)
def swc (request, webargs):
  """Get put interface for swc tracing files"""
  
  try:
    if request.method == 'GET':
      fname = "".join([x if x.isalnum() else "_" for x in webargs])
      response = django.http.HttpResponse(ocpcarest.getSWC(webargs), content_type="product/swc" )
      response['Content-Disposition'] = "attachment; filename={}.swc".format(fname)
      return response
    elif request.method == 'POST':
      return django.http.HttpResponse(ocpcarest.putSWC(webargs,request.body))
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in SWC.")
    raise

def annotation (request, webargs):
  """Get put object interface for RAMON objects"""
  
  [token, channel, rest] = webargs.split('/',2)

  try:
    if request.method == 'GET':
      return django.http.HttpResponse(ocpcarest.getAnnotation(webargs), content_type="product/hdf5" )
    elif request.method == 'POST':
      #if service == 'hdf5_async':
        #return django.http.HttpResponse( ocpcarest.putAnnotationAsync(webargs,request.body) )
      #else:
      return django.http.HttpResponse(ocpcarest.putAnnotation(webargs,request.body))
    elif request.method == 'DELETE':
      ocpcarest.deleteAnnotation(webargs)
      return django.http.HttpResponse ("Success", content_type='text/html')
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in annotation")
    raise OCPCAError("Unknown exception in annotation")


#@cache_control(no_cache=True)
def csv (request, webargs):
  """Get (not yet put) csv interface for RAMON objects"""

  try:
    if request.method == 'GET':
      return django.http.HttpResponse(ocpcarest.getCSV(webargs), content_type="text/html" )
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in csv")
    raise OCPCAError("Unknown exception in csv")


#@cache_control(no_cache=True)
def queryObjects ( request, webargs ):
  """Return a list of objects matching predicates and cutout"""

  try:
    if request.method == 'GET':
      return django.http.HttpResponse(ocpcarest.queryAnnoObjects(webargs), content_type="product/hdf5") 
    elif request.method == 'POST':
      return django.http.HttpResponse(ocpcarest.queryAnnoObjects(webargs,request.body), content_type="product/hdf5") 
    
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in listObjects")
    raise OCPCAError("Unknown exception in listObjects")


def catmaid (request, webargs):
  """Convert a CATMAID request into an cutout."""
  
  try:
    catmaidimg = ocpcarest.ocpcacatmaid_legacy(webargs)

    fobj = cStringIO.StringIO ( )
    catmaidimg.save ( fobj, "PNG" )
    fobj.seek(0)
    return django.http.HttpResponse(fobj.read(), content_type="image/png")

  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in catmaid {}.".format(e))
    raise OCPCAError("Unknown exception in catmaid {}.".format(e))


#@cache_control(no_cache=True)
def publictokens (request, webargs):
  """Return list of public tokens"""
  try:  
    return django.http.HttpResponse(ocpcarest.publicTokens(webargs), content_type="application/json" )
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in publictokens")
    raise OCPCAError("Unknown exception in publictokens")


#@cache_control(no_cache=True)
def jsoninfo (request, webargs):
  """Return project and dataset configuration information"""

  try:  
    return django.http.HttpResponse(ocpcarest.jsonInfo(webargs), content_type="application/json" )
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in jsoninfo")
    raise OCPCAError("Unknown exception in jsoninfo")

#@cache_control(no_cache=True)
def projinfo (request, webargs):
  """Return project and dataset configuration information"""
  
  try:  
    return django.http.HttpResponse(ocpcarest.projInfo(webargs), content_type="product/hdf5" )
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in projInfo")
    raise OCPCAError("Unknown exception in projInfo")

#@cache_control(no_cache=True)
#def chaninfo (request, webargs):
  #"""Return channel information"""

  #try:  
    #return django.http.HttpResponse(ocpcarest.chanInfo(webargs), content_type="application/json" )
  #except OCPCAError, e:
    #return django.http.HttpResponseNotFound(e.value)
  #except MySQLdb.Error, e:
    #return django.http.HttpResponseNotFound(e)
  #except:
    #logger.exception("Unknown exception in chanInfo")
    #raise OCPCAError("Unknown exception in chanInfo")


def mcFalseColor (request, webargs):
  """Cutout of multiple channels with false color rendering"""

  try:
    return django.http.HttpResponse(ocpcarest.mcFalseColor(webargs), content_type="image/png" )
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in mcFalseColor")
    raise OCPCAError("Unknown exception in mcFalseColor")

#@cache_control(no_cache=True)
def reserve (request, webargs):
  """Preallocate a range of ids to an application."""

  try:  
    return django.http.HttpResponse(ocpcarest.reserve(webargs), content_type="application/json" )
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in reserve")
    raise OCPCAError("Unknown exception in reserve")

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
    logger.exception("Unknown exception in setField")
    raise OCPCAError("Unknown exception in setField")

#@cache_control(no_cache=True)
def getField (request, webargs):
  """Get an individual RAMON field for an object"""

  try:
    return django.http.HttpResponse(ocpcarest.getField(webargs), content_type="text/html" )
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in getField")
    raise OCPCAError("Unknown exception in getField")

#@cache_control(no_cache=True)
def getPropagate (request, webargs):
  """ Get the value for Propagate field for a given project """

  try:
    return django.http.HttpResponse(ocpcarest.getPropagate(webargs), content_type="text/html" )
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in getPropagate")
    raise OCPCAError("Unknown exception in getPropagate")

def setPropagate (request, webargs):
  """ Set the value for Propagate field for a given project """

  try:
    ocpcarest.setPropagate(webargs)
    return django.http.HttpResponse()
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in setPropagate")
    raise OCPCAError("Unknown exception in setPropagate")

def merge (request, webargs):
  """Merge annotation objects"""

  try:
    return django.http.HttpResponse(ocpcarest.merge(webargs), content_type="text/html" )
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in global Merge")
    raise OCPCAError("Unknown exception in global Merge")

def exceptions (request, webargs):
  """Return a list of multiply labeled pixels in a cutout region"""

  try:
    return django.http.HttpResponse(ocpcarest.exceptions(webargs), content_type="product/hdf5" )
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in exceptions Web service")
    raise OCPCAError("Unknown exception in exceptions Web service")

#@cache_control(no_cache=True)
def minmaxProject (request, webargs):
  """Restful URL for all read services to annotation projects"""
 
  try:
    return django.http.HttpResponse(ocpcarest.minmaxProject(webargs), content_type="image/png" )
  except OCPCAError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except:
    logger.exception("Unknown exception in (min|max) projection Web service")
    raise OCPCAError("Unknown exception in (min|max) projection Web service")

def createProject(request, webargs):
  """RESTful URL for creating a project using a JSON file"""

  try:
    return django.http.HttpResponse(jsonproj.createProject(webargs, request.body), content_type="application/json")
  except OCPCAError, e:
    return django.http.HttpResponseNotFound()
  except:
    logger.exception("Unknown exception in jsonProject Web service")
    raise OCPCAError("Unknown exception in jsonProject Web service")

def createChannel(request, webargs):
  """RESTful URL for creating a list of channels using a JSON file"""

  try:
    return django.http.HttpResponse(jsonproj.createChannel(webargs, request.body), content_type="application/json")
  except OCPCAError, e:
    return django.http.HttpResponseNotFound()
  except:
    logger.exception("Unknown exception in jsonProject Web service")
    raise OCPCAError("Unknown exception in jsonProject Web service")

def deleteChannel(request, webargs):
  """RESTful URL for deleting a list of channels using a JSON file"""

  try:
    return django.http.HttpResponse(jsonproj.deleteChannel(webargs, request.body), content_type="application/json")
  except OCPCAError, e:
    return django.http.HttpResponseNotFound()
  except:
    logger.exception("Unknown exception in jsonProject Web service")
    raise OCPCAError("Unknown exception in jsonProject Web service")
