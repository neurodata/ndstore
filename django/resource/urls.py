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

from django.conf.urls import url
from publicview import DatasetPublicView, ProjectPublicView, TokenPublicView
from datasetview import DatasetView
from listview import DatasetListView, ProjectListView
from projectview import ProjectView
from channelview import ChannelView
from tokenview import TokenView

urlpatterns = [
  url(r'public/dataset/?$', DatasetPublicView.as_view()),
  url(r'public/token/?$', TokenPublicView.as_view()),
  url(r'public/dataset/?P(<dataset_name>[\w_-]+)/?$', ProjectPublicView.as_view()),
  url(r'dataset/?$', DatasetListView.as_view()),
  url(r'dataset/(?P<dataset_name>[\w_-]+)/?$', DatasetView.as_view()),
  url(r'dataset/(?P<dataset_name>[\w_-]+)/project/?$', ProjectListView.as_view()),
  url(r'dataset/(?P<dataset_name>[\w_-]+)/project/(?P<project_name>[\w_-]+)/?$', ProjectView.as_view()),
  url(r'dataset/(?P<dataset_name>[\w_-]+)/project/(?P<project_name>[\w_-]+)/channel/(?P<channel_name>[\w_-]+)/?$', ChannelView.as_view()),
  url(r'dataset/(?P<dataset_name>[\w_-]+)/project/(?P<project_name>[\w_-]+)/token/(?P<token_name>[\w_-]+)/?$', TokenView.as_view()),
]
