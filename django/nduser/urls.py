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

from django.conf.urls import *
from . import views
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^profile/$', views.getProjects),
    url(r'^projects/$', views.getProjects),
    url(r'^datasets/$', views.getDatasets),
    url(r'^channels/$', views.getChannels),
    url(r'^token/$', views.getTokens),
    url(r'^alltokens/$', views.getAllTokens),
    url(r'^createproject/$', views.createProject),
    url(r'^createdataset/$', views.createDataset),
    url(r'^createtoken/$', views.createToken),
    url(r'^updateproject/$', views.updateProject),
    url(r'^updatetoken/$', views.updateToken),
    url(r'^updatechannel/$', views.updateChannel),
    url(r'^updatedataset/$', views.updateDataset),
    url(r'^backupproject/$', views.backupProject),
    url(r'^restoreproject/$', views.restoreProject),
    url(r'^download/$', views.downloadData),
    url(r'^usertoken/$', views.getUserToken),
    url(r'^$', views.default)
]
