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

from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authtoken.models import Token

import django.http
from django.views.decorators.cache import cache_control
import MySQLdb
import cStringIO
import re
import json
from rest_framework.permissions import AllowAny

from django.conf import settings
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate
from jsonschema import validate, ValidationError, SchemaError

import logging
logger=logging.getLogger("neurodata")

USER_SCHEMA={
  "type": "object",
  "properties": {
    "user": {
      "type": "string",
      "pattern": "(?=^[^$&+,:;=?@#|'<>.^*()%!-]+$)(?=^[a-zA-Z0-9_]*$)"
    },
    "password": {
      "type": "string",
      "pattern": "(?=^[^$&+,:;=?@#|'<>.^*()%!-]+$)(?=^[a-zA-Z0-9]*$)"
    },
    "secret": {
      "type": "string",
      "pattern": "(?=^[^$&+,:;=?@#|'<>.^*()%!-]+$)(?=^[a-zA-Z0-9]*$)"
    },
  }, 
  "required": ["user","password","secret"]
}

# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny,])
def validate(request, webargs):
  """Restful URL to Validate User Credentials"""
  import pdb; pdb.set_trace()
  try:
    credentials = json.loads(request.body)
    validate(credentials, USER_SCHEMA)
    assert(credentials["secret"], settings.SHARED_SECRET)

  except AssertionError as e:
    logger.warning("Incorrect shared secret for user {} from {}".format(credentials["user"], request.get_host()))
    return HttpResponseForbidden()

  except ValueError as e:
    logger.warning("Error in decoding Json in NDAUTH: \
{}".format(e))
    return HttpResponseForbidden()

  except ValidationError as e:
    logger.warning("Error in validating Json against USER_SCHEMA: \
{}".format(e))
    return HttpResponseForbidden()

  user = authenticate(username=credentials["user"], password=credentials["password"])
  if user is not None:
    token = Token.objects.filter(user=request.user.id)
    return HttpResponse(token)
  else:
    return HttpResponseForbidden()
