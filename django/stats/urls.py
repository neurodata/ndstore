# Copyright 2016 NeuroData (http://neurodata.io)
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
from . import views

urlpatterns = [
  # get all statistics
  url(r'(?P<webargs>^\w+/\w+/all/[\w,/]*)$', views.all),
  # get JSON representation of histogram given an ROI (or 404)
  url(r'(?P<webargs>^\w+/\w+/hist/roi/[\d,-]+)/$', views.getHistROI),
  # get binned (reduced by factor of 10) JSON representation of histogram given an ROI (or 404)
  url(r'(?P<webargs>^\w+/\w+/binnedhist/roi/[\d,-]+)/$', views.getBinnedHistROI),
  # get all ROIs w/ histograms for a given channel / token
  url(r'(?P<webargs>^\w+/\w+/hist/roi/)$', views.getROIs),
  # get JSON representation of histogram given an ROI (or 404)
  url(r'(?P<webargs>^\w+/\w+/hist/[\w,/]*)$', views.getHist),
  # get mean
  url(r'(?P<webargs>^\w+/\w+/mean/[\w,/]*)$', views.mean),
  # get standard deviation
  url(r'(?P<webargs>^\w+/\w+/std/[\w,/]*)$', views.std),
  # get percentile
  url(r'(?P<webargs>^\w+/\w+/percentile/[\w,/.]*)$', views.percentile),
  # generate histogram (POST and GET)
  url(r'(?P<webargs>^\w+/\w+/genhist/[\w,/]*)$', views.genHist),
]
