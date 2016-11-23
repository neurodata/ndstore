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

import pickle
from nduser.models import NIFTIHeader
from ndproj.ndobject import NDObject

class NDNiftiHeader(object):

  def __init__(self, nh):
    self._nh = nh

  @classmethod
  def fromJson(cls, nifti_header):
    nh = NiftiHeader(**cls.deserialize(nifti_header))
    return cls(nh)
  
  @classmethod
  def fromImage(cls, ch, nifti_image):
    nh = NIFTIHeader(channel_id = ch.channel_id, header=pickle.dumps(nifti_image.header), affine=pickle.dumps(nifti_image.affine))
    return cls(nh)
  
  @classmethod
  def fromChannel(cls, ch):
    nh = NIFTIHeader.objects.get(channel_id=ch.channel_id)
    return cls(nh)

  def save(self):
    try:
      self._nh.save()
    except Exception as e:
      raise

  def delete(self):
    try:
      self._nh.delete()
    except Exception as e:
      raise

  @property
  def channel(self):
    return self._nh.channel

  @property
  def header(self):
    try:
      return pickle.loads(self._nh.header)
    except Exception as e:
      return None

  @property
  def affine(self):
    try:
      return pickle.loads(self._nh.affine)
    except Exception as e:
      return None
