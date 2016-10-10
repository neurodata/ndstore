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
from ndproject import NDProject

class ProjectView(View):

  def get(self, request, dataset_name, project_name):
    try:
      pr = NDProject.fromName(project_name)
      return HttpResponse(NDProject.serialize(pr.pr), content_type='application/json')
    except Exception as e:
      return HttpResponseBadRequest()

  def post(self, request, dataset_name, project_name):
    try:
      pr = NDProject.fromJson(dataset_name, request.body)
      if request.user.is_authenticated:
        pr.user_id = request.user.id
      else:
        pr.user_id = User.objects.get(username='neurodata').id
      pr.save()
      return HttpResponse()
    except Exception as e:
      return HttpResponseBadRequest()

  def put(self, request, web_args):
    return NotImplemented

  def delete(self, request, dataset_name, project_name):
    try:
      pr = NDProject.fromName(project_name)
      pr.delete()
      return HttpResponse()
    except Exception as e:
      return HttpResponseBadRequest()
