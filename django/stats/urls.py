# Copyright 2015 NeuroData (http://neurodata.io)
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
from stats import views

urlpatterns = [
  # get all statistics
  url(r'(?P<webargs>^\w+/\w+/all/[\w,/]*)$', views.all),
  # get JSON representation of histogram (or 404)
  url(r'(?P<webargs>^\w+/\w+/hist/[\w,/]*)$', views.getHist),
  # get mean 
  url(r'(?P<webargs>^\w+/\w+/mean/[\w,/]*)$', views.mean),
  # get standard deviation 
  url(r'(?P<webargs>^\w+/\w+/std/[\w,/]*)$', views.std),
  # get percentile 
  url(r'(?P<webargs>^\w+/\w+/percentile/[\w,/.]*)$', views.percentile),
  # generate histogram  
  url(r'(?P<webargs>^\w+/\w+/genhist/[\w,/]*)$', views.genHist),
]
