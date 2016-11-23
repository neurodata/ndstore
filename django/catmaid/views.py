# Copyright 2014 NeuroData (http://neurodata.io)
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

import re
import django.http
import mcfccatmaid
import simplecatmaid
import maxprojcatmaid
from webservices.ndwserror import NDWSError

import logging
logger = logging.getLogger("neurodata")

def filterview (request, webargs):
  """filtered ids false color"""

  try:
    fv = filtercatmaid.FilterCatmaid()
    imgfobj = fv.getTile(webargs)
    return django.http.HttpResponse(imgfobj.read(), content_type="image/png")

  except NDWSError, e:
    return django.http.HttpResponseNotFound(e)
  except Exception, e:
    logger.exception("Unknown exception in filtercatmaidview: {}".format(e) )
    raise

def maxprojview (request, webargs):
  """multi-channel false color"""

  try:
    mp = maxprojcatmaid.MaxProjCatmaid()
    imgfobj = mp.getTile(webargs)
    return django.http.HttpResponse(imgfobj.read(), content_type="image/png")

  except NDWSError, e:
    return django.http.HttpResponseNotFound(e)
  except Exception, e:
    logger.exception("Unknown exception in mcfccatmaidview: {}".format(e) )
    raise


def mcfccatmaidview (request, webargs):
  """multi-channel false color"""

  try:
    mc = mcfccatmaid.MCFCCatmaid()
    imgfobj = mc.getTile(webargs)
    return django.http.HttpResponse(imgfobj.read(), content_type="image/png")

  except NDWSError, e:
    return django.http.HttpResponseNotFound(e)
  except Exception, e:
    logger.exception("Unknown exception in mcfccatmaidview: {}".format(e))
    raise

def simplecatmaidview (request, webargs):
  """Convert a CATMAID request into an cutout."""
  
  try:
    sc = simplecatmaid.SimpleCatmaid()
    imgfobj = sc.getTile(webargs)
    return django.http.HttpResponse(imgfobj.read(), content_type="image/png")

  except NDWSError, e:
    return django.http.HttpResponseNotFound(e)
  except Exception, e:
    logger.exception("Unknown exception in simplecatmaidview: {}".format(e))
    raise

def simplevikingview (request, webargs):
  """Convert a Viking request into a simple catmaid cutout."""
  
  try:
    # argument of format token/volume/channel/resolution/Xtile_Ytile_Ztile
    m = re.match(r'(\w+)/volume/(\w+)/(\d+)/X(\d+)_Y(\d+)_Z(\d+).png$', webargs)
    [token, channel, resolution, xtile, ytile, ztile] = [i for i in m.groups()]

    # rewriting args here into catmaid format token/channel/slice_type/z/y_x_res.png
    webargs = '{}/{}/xy/{}/{}_{}_{}.png'.format(token, channel, ztile, ytile, xtile, resolution)

    sc = simplecatmaid.SimpleCatmaid()
    imgfobj = sc.getTile(webargs)
    response = django.http.HttpResponse(imgfobj.read(), content_type="image/png")
    response['content-length'] = len(response.content)
    return response

  except NDWSError, e:
    return django.http.HttpResponseNotFound(e)
  except Exception, e:
    logger.exception("Unknown exception in simplecatmaidview: {}".format(e) )
    raise
