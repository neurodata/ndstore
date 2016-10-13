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

from django.views.generic import View
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest
import pdb; pdb.set_trace()
from ingestmanager import IngestManager

class IngestView(View):

  def get(self, request, web_args):
    return NotImplemented

  def post(self, request):
    try:
      ingest_manager = IngestManger()
      return HttpResponse(ingest_manager.createIngestJob(request.body), content_type='application/json')
    except Exception as e:
      return HttpResponseBadRequest()

  def delete(self, request, web_args):
    return NotImplemented
