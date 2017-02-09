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
import MySQLdb
import cStringIO
import django.http
from django.shortcuts import render
from django.views.decorators.cache import cache_control
import webservices.ndwsjson
import webservices.ndwsprojingest
from webservices.ndwserror import NDWSError
import logging
logger = logging.getLogger("neurodata")


def jsonramon (request, webargs):
  """Get put object interface for JSON-ified RAMON objects"""

  [token, channel, rest] = webargs.split('/',2)

  try:
    if request.method == 'GET':
      return django.http.HttpResponse(ndwsjson.getAnnotation(webargs), content_type="application/json" )
#    elif request.method == 'POST':
#      return django.http.HttpResponse(ndwsjson.putJSONAnnotation(webargs,request.body))
#    elif request.method == 'DELETE':
#      print "JSON delete"
#      ndwsjson.deleteAnnotation(webargs)
#      return django.http.HttpResponse ("Success", content_type='text/html')
  except NDWSError, e:
    return django.http.HttpResponseNotFound(e.value)
  except MySQLdb.Error, e:
    return django.http.HttpResponseNotFound(e)
  except Exception, e:
    logger.exception("Unknown exception in jsonramon. {}".format(e))
    raise NDWSError("Unknown exception in jsonramon. {}".format(e))


def jsonquery (request, webargs):
  """Query ids that match a key/value pair"""

  if request.method == 'GET':
    return django.http.HttpResponse(ndwsjson.query(webargs), content_type="application/json" )
  else:
    logger.exception("Unsupported request method in query.  Only GET for now.")
    raise NDWSError("Unsupported request method in query.  Only GET for now.")
  

def topkeys (request, webargs):
  """Return the top 10 keys or some other number that is user specified"""

  if request.method == 'GET':
    return django.http.HttpResponse(ndwsjson.topkeys(webargs), content_type="application/json" )
  else:
    logger.exception("Unsupported request method in topkeys.  Only GET.")
    raise NDWSError("Unsupported request method in topkeys.  Only GET for now.")

