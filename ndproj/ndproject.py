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
from django.conf import settings

from nduser.models import Dataset
from nduser.models import Project
from nduser.models import Channel
from nduser.models import Token

from nddataset import NDDataset
from ndchannel import NDChannel

from ndwserror import NDWSError
import logging
logger=logging.getLogger("neurodata")

class NDProject:

  def __init__(self, token_name ) :

    if isinstance(token_name, str) or isinstance(token_name, unicode):
      try:
        self.tk = Token.objects.get(token_name = token_name)
        self.pr = Project.objects.get(project_name = self.tk.project_id)
        self.datasetcfg = NDDataset(self.pr.dataset_id)
      except ObjectDoesNotExist, e:
        logger.error("Token {} does not exist. {}".format(token_name, e))
        raise NDWSError("Token {} does not exist".format(token_name))
    elif isinstance(token_name, Project):
      # Constructor for NDProject from Project Name
      try:
        self.tk = None
        self.pr = token_name
        self.datasetcfg = NDDataset(self.pr.dataset_id)
      except ObjectDoesNotExist, e:
        logger.error("Token {} does not exist. {}".format(token_name, e))
        raise NDWSError("Token {} does not exist".format(token_name))

  # Accessors
  def getToken ( self ):
    return self.tk.token_name
  def getDBHost ( self ):
      return self.pr.host
  def getKVEngine ( self ):
    return self.pr.kvengine
  def getKVServer ( self ):
    return self.pr.kvserver
  def getMDEngine ( self ):
    return self.pr.mdengine
  def getDBName ( self ):
    return self.pr.project_name
  def getProjectName ( self ):
    return self.pr.project_name
  def getProjectDescription ( self ):
    return self.pr.project_description
  def getNDVersion ( self ):
    return self.pr.nd_version
  def getSchemaVersion ( self ):
    return self.pr.schema_version

  def projectChannels ( self, channel_list=None ):
    """Return a generator of Channel Objects"""
    if channel_list is None:
      chs = Channel.objects.filter(project_id=self.pr)
    else:
      chs = channel_list
    for ch in chs:
      yield NDChannel(self, ch.channel_name)

  def getChannelObj ( self, channel_name='default' ):
    """Returns a object for that channel"""
    if channel_name == 'default':
      channel_name = Channel.objects.get(project_id=self.pr, default=True)
    return NDChannel(self, channel_name)

  def getDBUser( self ):
    return settings.DATABASES['default']['USER']
  def getDBPasswd( self ):
    return settings.DATABASES['default']['PASSWORD']
  
  def deleteProject(self):
    """Delete the Project"""
    self.pr.delete()
