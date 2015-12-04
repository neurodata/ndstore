# Copyright 2014 Open Connectome Project (http://openconnecto.me)
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
urlpatterns = patterns('spdb.views',
  # catmaid
  url(r'^catmaid/(?P<webargs>\w+/.*)$', 'catmaid'),
  # nifti -- volumetric 3-d and 4-d
  url(r'(?P<webargs>^\w+/[\w+,/]*nii/[\w,/]*)$', 'nifti'),
  # swc -- annotations file get and put
  url(r'(?P<webargs>^\w+/[\w+,/]*swc/[\w,/]*)$', 'swc'),
  # fetch ids (with predicates)
  url(r'(?P<webargs>^\w+/\w+/query/[\w\.,/]*)$', 'queryObjects'),
  # get project information
  url(r'(?P<webargs>^\w+/projinfo/[\w,/]*)$', 'projinfo'),
  url(r'(?P<webargs>^\w+/info/[\w,/]*)$', 'jsoninfo'),
  url(r'(?P<webargs>^\w+/volume.vikingxml)$', 'xmlinfo'),
  # get public tokens 
  url(r'(?P<webargs>^public_tokens/)$', 'publictokens'),
  # Create/Delete channel interfaces
  url(r'(?P<webargs>^\w+/createChannel/)$', 'createChannel'),
  url(r'(?P<webargs>^\w+/deleteChannel/)$', 'deleteChannel'),
  # get channel information
  #url(r'(?P<webargs>^\w+/chaninfo/[\w,/]*)$', 'chaninfo'),
  # reserve identifiers for annotation projects
  url(r'(?P<webargs>^\w+/\w+/reserve/[\w+,/]*)$', 'reserve'),
  # get list of multiply labelled voxels in a cutout region
  url(r'(?P<webargs>^\w+/exceptions/[\w,/]*)$', 'exceptions'),
  # projection services
  url(r'(?P<webargs>^\w+/(minproj|maxproj)/(xy|xz|yz)[\w,/]*)$', 'minmaxProject'),
  # get services
  url(r'(?P<webargs>^\w+/[\w+,/]*(xy|xz|yz|tiff|hdf5|blosc|jpeg|npz|zip|diff|id|ids|xyanno|xzanno|yzanno)/[\w,/-]+)$', 'cutout'),
  # single field interfaces
  url(r'(?P<webargs>^\w+/\w+/getField/\d+/[\w+,/]*)$', 'getField'),
  url(r'(?P<webargs>^\w+/\w+/setField/\d+/[\w+,./]*)$', 'setField'),
  # propagate interfaces
  url(r'(?P<webargs>^\w+/[\w+,]+/getPropagate/)$', 'getPropagate'),
  url(r'(?P<webargs>^\w+/[\w+,]+/setPropagate/[\d+,]+/)$', 'setPropagate'),
  # merge annotations
  url(r'(?P<webargs>^\w+/\w+/merge/[\w,/]+)$', 'merge'),
  # csv metadata read
  url(r'(?P<webargs>^\w+/(csv)[\d+/]?[\w,/]*)$', 'csv'),
  # multi-channel false color image
  url(r'(?P<webargs>^\w+/mcfc/[\w,/-]+)$', 'mcFalseColor'),
  # HDF5 interfaces
  url(r'(?P<webargs>^\w+/\w+/[\d+/]?[\w,/]*)$', 'annotation'),
  # JSON interfaces
  url(r'(?P<webargs>^autoIngest/)$', 'autoIngest'),
)
