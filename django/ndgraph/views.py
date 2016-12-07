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

# Create your views here.
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.files.base import ContentFile
from wsgiref.util import FileWrapper
import re
from contextlib import closing
from nduser.models import Token
from webservices.ndwserror import NDWSError
import ndgraph
import logging
logger=logging.getLogger("neurodata")

#@login_required(login_url='/nd/accounts/login/')
@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def buildGraph (request, webargs):
    """Build a graph based on different arguments"""
    
    try:
      # TODO UA use regex here verus replace. Check ndwsrest for more details.
      args = (webargs.replace(',','/').split('/'))[0:-1]
      w_token = args[0]
      
      # TODO UA this will be replaced by NDToken and authentication
      if not request.user.is_superuser:
        m_tokens = Token.objects.filter(user=request.user.id) | Token.objects.filter(public=1)
        tokens = []
        for v in m_tokens.values():
          tokens.append(v['token_name'])
        if w_token not in tokens:
          logger.error("Token {} does not exist or you do not have sufficient permissions to access it.".format(w_token))
          raise NDWSError("Token {} does not exist or you do not have sufficient permissions to access it.".format(w_token))
        
      # TODO UA where are you closing this file. we need to ensure that this file is closed before it is returned.
      (file, filename) = ndgraph.genGraphRAMON (*args)
      response = HttpResponse(content_type='text/plain')
      response['Content-Disposition'] = "attachment; filename=\"output.{}\"".format(filename)
      response.write(file.read())
      return response
    
    except Exception as e:
      logger.error(e)
      raise NDWSError(e)
