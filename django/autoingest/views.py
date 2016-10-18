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
from ingestmanager import IngestManager

class IngestView(View):

  def get(self, request, job_id):
    try:
      ingest_manager = IngestManager()
      return HttpResponse(ingest_manager.getIngestJob(job_id), content_type='application/json')
    except Exception as e:
      return HttpResponseBadRequest()

  def post(self, request):
    try:
      import pdb; pdb.set_trace()
      ingest_manager = IngestManager()
      if request.user.is_authenticated():
        return HttpResponse(ingest_manager.createIngestJob(request.user.id, request.body), content_type='application/json')
      else:
        user_id = User.objects.get(username='neurodata').id
        return HttpResponse(ingest_manager.createIngestJob(user_id, request.body), content_type='application/json', status=201)
    except Exception as e:
      return HttpResponseBadRequest()

  def delete(self, request, job_id):
    try:
      ingest_manager = IngestManager()
      ingest_manager.deleteIngestJob(job_id)
      return HttpResponse(status=204)
    except Exception as e:
      return HttpResponseBadRequest()
