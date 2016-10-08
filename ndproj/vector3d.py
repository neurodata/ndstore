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

class Vector3D(object):

  def __init__(self, dim_list):
    self._x = dim_list[0]
    self._y = dim_list[1]
    self._z = dim_list[2]
  
  @property
  def values(self):
    return [self._x, self._y, self._z]
  
  @property
  def x(self):
    return self._x

  @property
  def y(self):
    return self._y

  @property
  def z(self):
    return self._z
