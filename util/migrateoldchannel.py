# Copyright 2015 Open Connectome Project (http://openconnecto.me)
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

""" This script allows a user to migrate an oldchannel database to the new schema. 
Specifically, given an existing database and a new project, it creates all the existing channels
in the new project. It then runs the SQL queries to copy data into the new channels. 

Note: Be sure that the existing channels are in a SEPARATE project from the new channels. 
Otherwise, data loss WILL occur!!
"""

import os
import sys
import argparse
import MySQLdb
import time 

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'

import django
from django.conf import settings
django.setup()

from ocpuser.models import Project
from ocpuser.models import Token
from ocpuser.models import Channel
from ocpuser.models import Dataset
from django.contrib.auth.models import User

import ocpcaproj 

DATATYPE = { 1:['image','uint8'], 2:['annotation','uint32'], 3:['oldchannel','uint16'], 4:['oldchannel','uint8'], 5:['image','uint32'], 6:['image','uint8'], 7:['annotation','uint64'], 8:['image','uint16'], 9:['image','uint32'], 10:['image','uint64'], 11:['timeseries','uint8'], 12:['timeseries','uint16'] }

class migrateOldchannel:

  def __init__(self, newproj, oldproj):
    """Init the class"""
    
    self.oldproject_name = oldproj
    self.newproject_name = newproj
    
    # establish a DB connection
    self.oldconn = ''
    self.newconn = ''
    self.connect()

    self.oldchannels = self.getOldChannelList()
  
    # user configurable (if desired). defaults should be fine
    self.propagate = 2 # could use 0 if data was not downsampled
    self.readonly = 1 # readonly true 
  
  def connect(self):
    self.oldconn = MySQLdb.connect(host=settings.DATABASES['default']['HOST'], user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db=self.oldproject_name)
    self.newconn = MySQLdb.connect(host=settings.DATABASES['default']['HOST'], user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db=self.newproject_name)

  def closeConnection(self):
    self.oldconn.close()
    self.newconn.close()

  def getOldChannelList(self):
    """ Get list of old channels and return it """
    oldchannels = {}
    
    cursor = self.oldconn.cursor()
    cursor.execute('SELECT * from channels')
    for row in cursor.fetchall():
      oldchannels[row[0]] = row[1]
    
    cursor.close()

    return oldchannels 

  def importChannels(self):
    """ Import channels from the old project to the new project. """
      
    # make sure the ocp project exists 
    pr = Project.objects.get(project_name=self.newproject_name)

    for channel in self.oldchannels.keys():
      ch = Channel()
      ch.project = pr
      ch.channel_name = channel
      ch.channel_description = 'Imported from oldchannel schema.'
      ch.channel_type = 'image'
      ch.resolution = 0 # all oldchannel types should be 16-bit images
      ch.propagate = self.propagate
      ch.channel_datatype = 'uint8'
      ch.readonly = self.readonly
      ch.exceptions = 0
      ch.startwindow = 0
      ch.endwindow = 0
      ch.default = False

      try:
        ch.save()
        pd = ocpcaproj.OCPCAProjectsDB()
        pd.newOCPCAChannel( pr.project_name, ch.channel_name )
        print "Created channel {}".format(channel)
      except Exception, e:
        print "[ERROR]: {}".format(e)
        exit() 

  def importData(self):
    # clone existing tables for each resolution
    # move cloned tables to new db
    tables = self._cloneTables()

    # run sql command to copy data out for each channel and for each scaling level 
    for channel in self.oldchannels.keys():
    
      print "Migrating {}".format(channel)
      for table in tables:
        sqlget = "SELECT zindex, cube FROM {}_clone WHERE channel = {}".format( table, self.oldchannels[channel] )
        sqlins = "INSERT INTO {}_{} VALUES (%s, %s)".format( channel, table )
        try:
          cursor = self.newconn.cursor()
          cursor.execute(sqlget)
          result = cursor.fetchall()
          for res in result:
            cursor.execute(sqlins, res)
          cursor.close()
          self.newconn.commit()
          print "Successfully migrated {}, {}".format(channel, table)
        except Exception, e: 
          self.newconn.rollback()
          print repr(e)


  def _cloneTables(self):
    cursor = self.oldconn.cursor()
  
    # get tables
    cursor.execute('SHOW TABLES')
    tables_raw = cursor.fetchall()
    tables = []

    for table_raw in tables_raw:
      table = table_raw[0]
      if table[:3] == 'res':
        tables.append(table)

    for table in tables:
      # get create syntax
      cursor.execute('SHOW CREATE TABLE {}'.format(table))
      create_text = cursor.fetchone()[1]
      # create clone table 
      clone_text = "CREATE TABLE `{}_clone`{}".format(table, create_text[14+len(table)+1:]) 
      cursor.execute(clone_text)
      # clone the table 
      cursor.execute("INSERT INTO `{}_clone` SELECT * FROM `{}`".format(table, table))
      print "Cloned table {}".format(table) 

      # move tables to new db
      cursor.execute("RENAME TABLE {}.{}_clone TO {}.{}_clone".format(self.oldproject_name, table, self.newproject_name, table))
      print "Moved table {}_clone to DB {}".format( table, self.newproject_name )

    cursor.close()
    
    return tables

def main():

  parser = argparse.ArgumentParser(description="Migrate oldchannel to new schema.")
  parser.add_argument('old_project', action='store', help='The name of the old project / DB')
  parser.add_argument('new_project', action='store', help='The name of the new OCP project (where channels will be created)')
  parser.add_argument('--agree', dest='agree', action='store_true', help='I understand running this script improperly will surely cause data loss!')
  parser.add_argument('--channels', dest='channels', action='store_true', help='Add this flag to migrate old channels (in single table) to new channels (separate tables).')
  parser.add_argument('--data', dest='data', action='store_true', help='Add this flag to migrate old channel data to new channel data. Note that you must have migrated channels first (or at the same time).')
  parser.add_argument('--test', dest='test', action='store_true')

  result = parser.parse_args()

  if (result.test):
    mo = migrateOldchannel(result.new_project, result.old_project)
    mo._cloneTables()
    return

  if (result.agree is not True):
    print "[ERROR]: You must agree that you have read and understand the following statement:\nRunning this script improperly will most surely cause data loss!"
    return;
  
  mo = migrateOldchannel(result.new_project, result.old_project)
 
  if (result.channels and result.data):
    print "Migrating channels and data from old schema..."
    # channels first 
    mo.importChannels()
    mo.importData()
  elif (result.channels):
    print "Migrating channels from old schema..."
    mo.importChannels()
  elif (result.data):
    print "Migrating data from old schema..."
    mo.importData()
  else:
    print "Nothing to do. Run with -h for help. Quitting..."

if __name__ == "__main__":
  main()
