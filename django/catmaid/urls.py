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

from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

# already have the ^catmaid stripped off
urlpatterns = patterns('catmaid.views',
  # viking
  url(r'^viking/(?P<webargs>.*)$', 'simplevikingview'),
  # mcfc
  url(r'^mcfc/(?P<webargs>.*)$', 'mcfccatmaidview'),
  # mcfc
  url(r'^maxproj/(?P<webargs>.*)$', 'maxprojview'),
  #url(r'^color/(?P<webargs>.*)$', 'colorcatmaidview'),
  url(r'^(?P<webargs>.*)$', 'simplecatmaidview'),
  # catmaid
)
