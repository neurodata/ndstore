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

import redis

from ndproject import NDProject
from ndchannel import NDChannel

from ndwserror import NDWSError
import logging
logger=logging.getLogger("neurodata")

class RedisProjectDB:
  """Database for the projects"""

  def __init__(self, project_name):
    """Create the database connection"""
    self.pr = NDProject(project_name)
    # Connect to the redis cluster


  def close (self):
    """Close the database connection"""
    pass


  def newNDProject(self):
    """Create the database for a project."""
    pass
  

  def newNDChannel(self, channel_name):
    """Create the tables for a channel."""
    pass


  def deleteNDProject(self):
    """Delete the database for a project"""
    pass


  def deleteNDChannel(self, channel_name):
    """Delete the keys for a channel"""
    # TODO KL delete using keys 
    pass 
