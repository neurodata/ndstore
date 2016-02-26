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

import riak

from ndchannel import NDChannel
from ndproject import NDProject

from ndwserror import NDWSError
import logging
logger=logging.getLogger("neurodata")

class RiakProjDB:

  def __init__(self, project_name):
    """Create the database connection"""
    self.pr = NDProject(project_name)
    # connect to Riak
    self.rcli = riak.RiakClient(host=self.pr.getKVServer(), pb_port=8087, protocol='pbc')
  
  
  def newNDProject(self, project_name):
    """Create the database for a project"""
    pass


  def newNDChannel(self, project_name, channel_name):
    """Create the tables for a channel"""
    
    ch = NDChannel(self.pr, channel_name)
    pass 
    # TODO KL figure out new schema for Riak
    # bucket = rcli.bucket_type("nd{}".format(proj.getProjectType())).bucket(proj.getDBName())
    # bucket.set_property('allow_mult',False)


  def deleteNDProject(self, project_name):
    """Delete the database for a project"""

    pass 
    # TODO KL figure out the new schema
    # bucket = rcli.bucket_type("nd{}".format(proj.getProjectType())).bucket(proj.getDBName())

    # key_list = rcli.get_keys(bucket)

    # for key_name in key_list:
      # bucket.delete(key_name)


  def deleteNDChannel(self, project_name, channel_name):
    """Delete the tables for a channel"""
    
    ch = NDChannel(self.pr, channel_name)
    # table_list = []
    # TODO KL 
    pass
