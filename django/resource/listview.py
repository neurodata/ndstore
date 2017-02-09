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

import json
from django.views.generic import View
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest
from ndproj.nddataset import NDDataset
from ndproj.ndproject import NDProject

class DatasetListView(View):

  def get(self, request):
    try:
      return HttpResponse(json.dumps(NDDataset.public_list()), content_type='application/json')
    except Exception as e:
      return HttpResponseBadRequest()

class ProjectListView(View):

  def get(self, request, dataset_name):
    try:
      return HttpResponse(json.dumps(NDProject.public_list()), content_type='application/json')
    except Exception as e:
      return HttpResponseBadRequest()

class ChannelListView(View):

  def get(self, request, dataset_name, project_name):
    try:
      return HttpResponse(json.dumps(NDProject.public_list()), content_type='application/json')
    except Exception as e:
      return HttpResponseBadRequest()

class TokenListView(View):

  def get(self, request, dataset_name, project_name):
    try:
      return HttpResponse(json.dumps(NDProject.public_list()), content_type='application/json')
    except Exception as e:
      return HttpResponseBadRequest()
