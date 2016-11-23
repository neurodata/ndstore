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
from ndproj.ndproject import NDProject
from ndproj.ndchannel import NDChannel
from webservices.ndwserror import NDWSError
import logging
logger=logging.getLogger("neurodata")

class RedisProjectDB:
  """Database for the projects"""

  def __init__(self, pr):
    """Create the database connection"""
    self.pr = pr
    # Connect to the redis cluster
    try:
      self.client = redis.StrictRedis(host=self.pr.host, port=6379, db=0)
      self.pipe = self.client.pipeline(transaction=False)
    except redis.ConnectionError as e:
      logger.error("Cannot connect to Redis server. {}".format(e))
      raise NDWSError("Cannot connect to Redis server. {}".format(e))
    except Exception as e:
      logger.error("Unknown error while connecting to Redis. {}".format(e))
      raise NDWSError("Unknown error while connecting to Redis. {}".format(e))

  def __del__(self):
    """Close the database connection"""
    self.close()

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
    
    # KL TODO Is this redundant?
    # project pattern to fetch all the keys with project_name
    project_pattern = "{}_*".format(self.pr.project_name)
    try:
      project_keys = self.client.keys(project_pattern)
      # delete all the keys with the pattern
      if project_keys:
        self.client.delete(*project_keys)
    except Exception as e:
      logger.error("Error in deleting Redis project {}. {}".format(self.pr.project_name, e))
      raise NDWSError("Error in deleting Redis project {}. {}".format(self.pr.project_name, e))


  def deleteNDChannel(self, channel_name):
    """Delete the keys for a channel"""
    
    # KL TODO Maybe do this as a transaction?
    # channel pattern to fetch all the keys with project_name_channel_name
    channel_pattern = "{}_{}_*".format(self.pr.project_name, channel_name)
    try:
      channel_keys = self.client.keys(channel_pattern)
      # delete all the keys with the pattern
      if channel_keys:
        self.client.delete(*channel_keys)
    except Exception as e:
      logger.error("Error in deleting channel {}. {}".format(channel_name, e))
      raise NDWSError("Error in deleting channel {}. {}".format(channel_name, e))
