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

from contextlib import closing
from django.views.generic import View
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest
from ndproj.ndproject import NDProject
from ndproj.ndtoken import NDToken
from ndproj.ndchannel import NDChannel
from webservices import ndwsskel

class SwcView(View):

  def get(self, request, token_name, channel_name, ids):
  
    try:
      proj = projdb.fromTokenName(token_name)
      ch = NDChannel.fromName(proj, channel_name)
      with closing (RamonDB(proj)) as db:
        # Make a named temporary file for the SWC
        with closing (tempfile.NamedTemporaryFile()) as tmpfile:
          # if skeleton ids are specified, use those
          if ids:
            skelids = map ( int, ids.rstrip('/').split(',') )
          # otherwise get all skeletons
          else:
            skelids=db.getKVQuery(ch, 'ann_type', ANNO_SKELETON)
          ndwsskel.querySWC ( tmpfile, ch, db, proj, skelids )
          tmpfile.seek(0)
          return tmpfile.read()
    except Exception as e:
      return HttpResponseBadRequest()

  def post(self, request, token_name, channel_name):
    try:
    
      [token, channel, service, optionsargs] = webargs.split('/',3)
      proj = projdb.fromTokenName(token)
      ch = NDChannel.fromName(proj, channel)
  
      with closing (RamonDB(proj)) as rdb:

        # Don't write to readonly channels
        if ch.getReadOnly() == READONLY_TRUE:
          logger.error("Attempt to write to read only channel {} in project. Web Args:{}".format(ch.getChannelName(), proj.getProjectName(), webargs))
          raise NDWSError("Attempt to write to read only channel {} in project. Web Args: {}".format(ch.getChannelName(), proj.getProjectName(), webargs))

        # Make a named temporary file for the HDF5
        with closing (tempfile.NamedTemporaryFile()) as tmpfile:
          tmpfile.write(request.body)
          tmpfile.seek(0)
          # Parse the swc file into skeletons
          swc_skels = ndwsskel.ingestSWC ( tmpfile, ch, rdb )
          return swc_skels
    except Exception as e:
      return HttpResponseBadRequest()

  def put(self, request, web_args):
    return HttpResponseBadRequest()

  def delete(self, request, dataset_name, project_name, token_name):
    return HttpResponseBadRequest()
