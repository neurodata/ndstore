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

from django.core.exceptions import ObjectDoesNotExist
from nduser.models import Token
from ndtype import *
from ndproject import NDProject
from ndobject import NDObject

class NDToken(NDObject):

  def __init__(self, tk):
    self._tk = tk
  
  @staticmethod
  def public_list():
    tokens = Token.objects.filter(public = PUBLIC_TRUE)
    return [t.token_name for t in tokens]

  @classmethod
  def fromJson(cls, project_name, token):
    tk = Token(**cls.deserialize(token))
    tk.project_id = project_name
    return cls(tk)
  
  @classmethod
  def fromName(cls, token_name):
    try:
      tk = Token.objects.get(token_name=token_name)
      return cls(tk)
    except ObjectDoesNotExist as e:
      raise
  
  def create(self):
    try:
      self._tk.save()
    except Exception as e:
      raise

  def delete(self):
    try:
      self._tk.delete()
    except Exception as e:
      raise

  @property
  def token_name(self):
    return self._tk.token_name
  
  @token_name.setter
  def token_name(self, value):
    self._tk.token_name = value

  @property
  def token_description(self):
    return self._tk.token_description
  
  @token_description.setter
  def token_description(self, value):
    self._tk.token_description = value

  @property
  def user_id(self):
    return self._tk.user_id

  @user_id.setter
  def user_id(self, value):
    self._tk.user_id = value
  
  @property
  def project_name(self):
    return self._tk.project_id

  @project_name.setter
  def project_name(self, value):
    
    self._tk.project_id = value

  # @property
  # def project(self):
    # return NDProject(self._tk.project)
  
  # @project.setter
  # def project(self, pr):
    # self._tk.project = pr.project_name

  @property
  def public(self):
    return self._tk.public

  @public.setter
  def public(self, value):
    self._tk.public = value
