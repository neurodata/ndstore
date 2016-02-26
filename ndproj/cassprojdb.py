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

import cassandra

from ndchannel import NDChannel
from ndproject import NDProject
from ndtype import ND_servermap

from ndwserror import NDWSError
import logging
logger=logging.getLogger("neurodata")

class CassProjectDB:
  """Database for the projects"""

  def __init__(self, project_name):
    """Create the database connection"""
    
    self.project_name = project_name
    self.pr = NDProject(project_name)
    server_address = ND_servermap[self.pr.getKVServer()]
    cluster = Cluster([server_address])
    self.session = cluster.connect()


  def close (self):
    """Close the database connection"""
    self.session.shutdown()

  
  def newNDProject(self, project_name):
    """Create the database for a project"""
      
    try:
      if self.server_address == 'localhost':  
        self.session.execute ("CREATE KEYSPACE {} WITH REPLICATION = {{ 'class' : 'SimpleStrategy', 'replication_factor' : 0 }}".format(self.pr.getProjectName()), timeout=30)
      else:
        self.session.execute ("CREATE KEYSPACE {} WITH REPLICATION = {{ 'class' : 'SimpleStrategy', 'replication_factor' : 1 }}".format(self.pr.getProjectName()), timeout=30)
    
    except Exception, e:
      self.pr.deleteProject()
      logger.error("Failed to create namespace for new project {}".format(self.project_name))
      raise NDWSError("Failed to create namespace for new project {}".format(self.project_name))
    
    finally:
      self.close()


  def newNDChannel(self, channel_name):
    """Create the tables for a channel"""

    ch = NDChannel(self.pr, channel_name)

    try:
      if ch.getChannelType() not in [TIMESERIES]:
        self.session.execute ( "CREATE table {} ( resolution int, zidx bigint, cuboid text, PRIMARY KEY ( resolution, zidx ) )".format(ch.getTable()), timeout=30)
    
    except Exception, e:
      ch.deleteChannel()
      logging.error("Failed to create table for channel {}".format(channel_name))
      raise NDWSError("Failed to create table for channel {}".format(channel_name))
    
    finally:
      self.close()


  def deleteNDDB(self):
    """Delete the database for the project"""

    try:
      self.session.execute ( "DROP KEYSPACE {}".format(self.pr.getProjectName()), timeout=30 )
    
    except Exception, e:
      logger.warning("Keyspace {} does not exist".format(self.project_name))
      pass
    
    finally:
      self.close()


  def deleteNDChannel (self, channel_name):
    """Delete the tables for a channel"""

    ch = NDChannel(self.pr, channel_name)
    table_list = []
    
    try:
      for table_name in table_list:
        self.session.execute("DROP table {}".format(ch.getTable()))
    
    except Exception, e:
      logger.warning("Table {} does not exist".format(ch.getTable()))
      pass
    
    finally:
      self.close()
