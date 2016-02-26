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

import MySQLdb
from contextlib import closing

from ndproject import NDProject
from ndchannel import NDChannel

class MySQLProjectDB:
  """Database for the projects"""

  def __init__(self):
    """Create the database connection"""
    # connect to the database
    self.pr = NDProject(project_name)

  def close (self):
    pass

  def newNDProject(self):
    """Create the database for a project"""
    
    with closing(MySQLdb.connect (host = self.pr.getDBHost(), user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db = settings.DATABASES['default']['NAME'])) as conn:
      with closing(conn.cursor()) as cursor:

        try:
          # create the database
          sql = "CREATE DATABASE {}".format(pr.project_name)
       
          cursor.execute(sql)
          conn.commit()
        
        except MySQLdb.Error, e:
          logger.error("Failed to create database for new project {}: {}. sql={}".format(e.args[0], e.args[1], sql))
          raise NDWSError("Failed to create database for new project {}: {}. sql={}".format(e.args[0], e.args[1], sql))
  

  def newNDChannel(self, channel_name):
    """Create the tables for a channel"""

    ch = NDChannel(channel_name)

    # Connect to the database

    with closing(MySQLdb.connect(host = self.pr.getDBHost(), user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db = self.pr.getDBName())) as conn:
      with closing(conn.cursor()) as cursor:
        
        try:
          # tables specific to all other non time data
          if ch.getChannelType() not in [TIMESERIES]:
            for res in self.pr.datasetcfg.getResolutions():
              cursor.execute("CREATE TABLE {} ( zindex BIGINT PRIMARY KEY, cube LONGBLOB )".format(ch.getTable(res) )
          # tables specific to timeseries data
          elif ch.getChannelType() == TIMESERIES:
            for res in self.pr.datasetcfg.getResolutions():
              cursor.execute("CREATE TABLE {} ( zindex BIGINT, timestamp INT, cube LONGBLOB, PRIMARY KEY(zindex,timestamp))".format(ch.getTable(res)))
          else:
            raise NDWSError("Channel type {} does not exist".format(ch.getChannelType()))
          
          # tables specific to annotation projects
          if ch.getChannelType() == ANNOTATION: 
            cursor.execute("CREATE TABLE {} ( id BIGINT PRIMARY KEY)".format(ch.getIdsTable()))
            # And the RAMON objects
            cursor.execute("CREATE TABLE {}_ramon ( annoid BIGINT, kv_key VARCHAR(255), kv_value VARCHAR(20000), PRIMARY KEY ( annoid, kv_key ))".format(ch.channel_name))
            for res in self.pr.datasetcfg.getResolutions():
              cursor.execute("CREATE TABLE {} ( zindex BIGINT, id BIGINT, exlist LONGBLOB, PRIMARY KEY ( zindex, id))".format(ch.getExceptionsTable(res)))
              cursor.execute("CREATE TABLE {} ( annid BIGINT PRIMARY KEY, cube LONGBLOB )".format(ch.getIdxTable(res))
         
          # Commiting at the end
          conn.commit()
        except MySQLdb.Error, e:
          ch.deleteChannel()
          logging.error ("Failed to create tables for new project {}: {}.".format(e.args[0], e.args[1]))
          raise NDWSError ("Failed to create tables for new project {}: {}.".format(e.args[0], e.args[1]))


  def deleteNDProject(self):
    """Delete the database for a project"""

    with closing(MySQLdb.connect (host = self.pr.getDBHost(), user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'])) as conn:
      with closing(conn.cursor()) as cursor:
        # delete the database
        sql = "DROP DATABASE {}".format(self.pr.getProjectName())

        try:
          cursor.execute(sql)
          conn.commit()
        except MySQLdb.Error, e:
          # Skipping the error if the database does not exist
          if e.args[0] == 1008:
            logger.warning("Database {} does not exist".format(pr.getProjectName()))
            pass
          else:
            conn.rollback()
            logger.error("Failed to drop project database {}: {}. sql={}".format(e.args[0], e.args[1], sql))
            raise NDWSError("Failed to drop project database {}: {}. sql={}".format(e.args[0], e.args[1], sql))


  def deleteNDChannel (self, proj, channel_name):
    """Delete the tables for this channel"""

    pr = NDProject(proj)
    ch = NDChannel(pr, channel_name)
    table_list = []

    if ch.getChannelType() in ANNOTATION_CHANNELS:
      table_list.append(ch.getIdsTable())
      for key in annotation.anno_dbtables.keys():
        table_list.append(ch.getAnnoTable(key))

    for res in self.pr.datasetcfg.getResolutions():
      table_list.append(ch.getTable(res))
      if ch.getChannelType() in ANNOTATION_CHANNELS:
        table_list = table_list + [ch.getIdxTable(res), ch.getExceptionsTable(res)]

    try:
      conn = MySQLdb.connect (host = pr.getDBHost(), user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db = pr.getProjectName()) 
      # delete the tables for this channel
      sql = "DROP TABLES IF EXISTS {}".format(','.join(table_list))
    
      with closing(conn.cursor()) as cursor:
        cursor.execute (sql)
        conn.commit()
    except MySQLdb.Error, e:
      # Skipping the error if the table does not exist
      if e.args[0] == 1051:
        pass
      if e.args[0] == 1049:
        pass
      else:
        conn.rollback()
        logger.error("Failed to drop channel tables {}: {}. sql={}".format(e.args[0], e.args[1], sql))
        raise NDWSError("Failed to drop channel tables {}: {}. sql={}".format(e.args[0], e.args[1], sql))
