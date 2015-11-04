# Copyright 2015 Open Connectome Project (http://openconnecto.me)
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
from ocpuser.views import *
import django.contrib.auth
  # ocp/viz/ramoninfo/<<server>>/<<token>>/<<channel>>/<<id>>/

urlpatterns = patterns('ocpviz.views',
    # data views
    url(r'^dataview/(?P<webargs>[\w:,/-]+)', 'dataview'),
    url(r'^public/$', 'dataviewsPublic'),
    # for redirecting queries (reqd because of same origin policy)
    url(r'^query/(?P<queryargs>[\w,/-]+)', 'query'),
    # for getting the projinfo json information from ocp
    url(r'^projinfo/(?P<queryargs>[\w,/-]+)', 'projinfo'),
    # for getting the ramon json information from ocp
    url(r'^ramoninfo/(?P<webargs>[\w,/-]+)', 'ramoninfo'),
    # validate token/channel/server
    url(r'^validate/(?P<webargs>[\w,\.,/-]+)', 'validate'),
    url(r'^$', 'default'),
    url(r'^manage/$', 'default'),
    # for displaying ocpviz projects 
    # NOTE: this must be last (because of the tokenview view)
    url(r'^project/(?P<webargs>[\w:,/-]+)', 'projectview'),
    url(r'(?P<webargs>[\w:,/-]+)$', 'tokenview'),
)
