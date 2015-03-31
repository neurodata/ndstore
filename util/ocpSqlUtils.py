# Copyright 2014 Open Connectome Project (http://openconnecto.me)
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

#
# SQL dump and ingest script for OCP databases. All projects and datasets supported.
#

import argparse
import sys
import os
import subprocess
from contextlib import closing

import MySQLdb

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings
import django
django.setup()


import ocpcaproj
import ocpcaprivate
import ocpcadb

class SQLDatabase:

  def __init__(self, host, token, channel, location):
    """ Load the database and project """

    with closing ( ocpcaproj.OCPCAProjectsDB() ) as projdb:
      self.proj = projdb.loadToken ( token )
    self.channels = self.proj.projectChannels()
    if self.channels is None:
      print "[ERROR]: No channels!" #ABTODO raise exception? 
      sys.exit(0)

    self.user = ocpcaprivate.dbuser
    self.password = ocpcaprivate.dbpasswd
    self.host = host
    self.token = token
    self.location = location
    self.starterString = '-u {} -p{} -h {}'.format( self.user, self.password, self.host )
    
    # get single channel if channel is not None
    if channel is not None:
      self.channel = self.proj.getChannelObj(channel_name=channel)

    try:
      self.db = MySQLdb.connect ( host = self.host, user = self.user, passwd = self.password, db = self.token ) 
      self.cur = self.db.cursor()    
    except MySQLdb.Error, e:
      print e

  def dumpBigTable( self, tableName ):
    """ Dump a very big Table """

    sql = "SELECT COUNT(*) FROM {}".format(tableName)
    self.cur.execute( sql )
    rowSize = self.cur.fetchone()
    cmd = 'mysqldump {}  -d {} {} > {}{}.{}_schema.sql'.format( self.starterString, self.token, tableName, self.location, self.token, tableName )
    os.system ( cmd )
    for i in range(0, rowSize[0], rowSize[0]/10):
        cmd = 'mysqldump {} {} {} --where "1 LIMIT {},{}" --no-create-info --skip-add-locks > {}{}.{}_{}.sql'.format ( self.starterString, self.token, tableName, i, (i-rowSize[0]) if (i-1+rowSize[0]/10) > rowSize[0] else (rowSize[0]/10), self.location, self.token, tableName, rowSize[0] if (i+rowSize[0]/10) > rowSize[0] else (i+  rowSize[0]/10) )
        print cmd
        os.system ( cmd )
    
    # Now ingesting this Big Table in the database

    cmd = 'mysql -ubrain -p88brain88 -h localhost {} < {}{}.{}_schema.sql'.format( self.token, self.location, self.token, tableName )
    print cmd
    os.system(cmd)
    for i in range(0, rowSize[0], rowSize[0]/10):
        cmd = 'mysql -h {} -u {} -p{} {} < {}{}.{}_{}.sql'.format ( "localhost", self.user, self.password, self.token, self.location, self.token, tableName, rowSize[0] if (i+rowSize[0]/10) > rowSize[0] else i+ rowSize[0]/10 )
        print cmd
        os.system( cmd )

  
  def copyTable ( self, newDBName ):
    """ Copy Tables from Database to another """

    sql = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE table_schema='{}'".format( self.token )

    self.cur.execute(sql)
    cur2 = self.db.cursor()

    for row in self.cur.fetchall():
      sql = "RENAME TABLE {}.{} TO {}.{}".format( self.token, row[0], newDBName, row[0] )
      print sql
      cur2.execute(sql)

    self.db.commit()

  def dumpSingleChannel( self ):
    """ Dump all resolutions of a single channel (anno, images, etc) """
    if self.channel.getChannelType() in ocpcaproj.ANNOTATION_CHANNELS:
      """ dump annotation """
      for i in range( 0, len(self.proj.datasetcfg.resolutions ) ):
        # channel tables
        ch_tables = [self.channel.getIDsTbl(), self.channel.getIdxTable(i)] 

        if self.channel.getExceptions():
          ch_tables.append(self.channel.getExceptions(i))

        cmd = 'mysqldump {} {} --tables {} > {}{}.{}.sql'.format ( self.starterString, self.token, ' '.join(ch_tables), self.location, self.token, self.channel.getTable(i) )
        print cmd
        os.system ( cmd )
    elif self.channel.getChannelType() in ocpcaproj.IMAGE_CHANNELS:
      """ dump image """
      for i in range( 0, len(self.proj.datasetcfg.resolutions ) ):
        cmd = 'mysqldump {} {} --tables {} > {}{}.{}.sql'.format ( self.starterString, self.token, self.channel.getTable(i), self.location, self.token, self.channel.getTable(i) )
        print cmd
        os.system ( cmd )
    else:
      errstr = "[ERROR]: Channel type {} is unsupported!".format(self.getChannelType())

  def dumpAllChannels( self ):
    """ Dump all resolutions for all project channels """
    for chan in self.channels:
      if chan.getChannelType() in ocpcaproj.ANNOTATION_CHANNELS:
        """ dump annotations """ 
        #TODO probably misssing RAMON object tables
        for i in range( 0, len(self.proj.datasetcfg.resolutions ) ):
          # channel tables
          ch_tables = [chan.getIDsTbl(), chan.getIdxTable(i)] 

          if chan.getExceptions():
            ch_tables.append(chan.getExceptions(i))

          cmd = 'mysqldump {} {} --tables {} > {}{}.{}.sql'.format ( self.starterString, self.token, ' '.join(ch_tables), self.location, self.token, chan.getTable(i) )
          print cmd
          os.system ( cmd )
      elif chan.getChannelType() in ocpcaproj.IMAGE_CHANNELS:
        """ dump image """
        for i in range( 0, len(self.proj.datasetcfg.resolutions ) ):
          cmd = 'mysqldump {} {} --tables {} > {}{}.{}.sql'.format ( self.starterString, self.token, chan.getTable(i), self.location, self.token, chan.getTable(i) )
          print cmd
          os.system ( cmd )
      else:
        errstr = "[ERROR]: Channel type {} is unsupported!".format(self.getChannelType())


  def ingestSingleChannel( self ):
    """ Ingest all resolutions of a single channel ( anno, images, etc ) """
    for i in range( 0, len(self.proj.datasetcfg.resolutions ) ):
      cmd = 'mysql {} {} < {}{}.{}.sql'.format ( self.starterString, self.token, self.location, self.token, self.channel.getTable(i) )
      print cmd
      os.system ( cmd )

  def ingestAllChannels( self ):
    """ Ingest all resolutions for all project channels """
    for chan in self.channels:
      for i in range( 0, len(self.proj.datasetcfg.resolutions ) ):
        cmd = 'mysql {} {} < {}{}.{}.sql'.format ( self.starterString, self.token, self.location, self.token, chan.getTable(i) )
        print cmd
        os.system ( cmd )

  def ingestImageStack ( self ):
    """ Ingest an Image Stack """

    for i in range(0, len(self.proj.datasetcfg.resolutions ) ):
      
      cmd = 'mysql {} {} < {}{}.res{}.sql'.format ( self.starterString, self.token, self.location, self.token, i )
      print cmd
      os.system( cmd )

  
  def ingestAnnotataionStack ( self ):
    """ Ingest an Annotation Stack """

    cmd = 'mysql {} {} < {}{}.sql'.format ( self.starterString, self.token, self.location, self.token )
    print cmd
    os.system( cmd )


  def ingestChannelStack ( self ):
    """ Ingest a Channel Stack """
      
    cmd = 'mysql {} {} < {}{}.{}.sql'.format ( self.starterString, self.token, self.location, self.token, "channels" )
    print cmd
    os.system( cmd )
    self.ingestImageStack()

def main():
  """ Parse Arguments from User """

  parser = argparse.ArgumentParser (description='Dump an Image Stack')
  parser.add_argument('host', action="store", help='HostName where to dump from')
  parser.add_argument('token', action="store", help='Token for the project.')
  parser.add_argument('location', action="store", help='Location where to store the dump[')
  parser.add_argument('--channel', dest='channel', action='store', default=None, help='Specify a channel (will dump all channels for the project if ignored)')
  parser.add_argument('--dump', dest='dump', action="store_true", help='Dump the database into a sqldump')
  parser.add_argument('--ingest', dest='ingest', action="store_true", help='Ingest the sqldump')
  parser.add_argument('--bigdump', dest='bigdump', help='Dump a big mysql table')
  parser.add_argument('--dbcopy', dest='dbcopy', action="store", default=None, help='Copy the database')
  parser.add_argument('--dbrename', dest='dbrename', action="store", default=None, help='Rename the database')

  result = parser.parse_args()
  
  if result.bigdump!=None:
    sqldb = SQLDatabase (  result.host, result.token, result.channel, result.location )
    sqldb.dumpBigTable ( result.bigdump ) 

  # Check for copy flag
  elif result.dbrename!=None:
    sqldb = SQLDatabase ( result.host, result.token, result.channel, result.location )
    sqldb.copyTable( result.dbrename )

  # Check for copy flag
  elif result.dbcopy!=None:

    sqldb = SQLDatabase ( result.host, result.token, result.channel, result.location )
    sqldb.dumpAllChannels()
    sqldb = SQLDatabase ( result.host, result.dbcopy, result.channel, result.location )
    sqldb.ingestImageStack() #ABTODO ingest all channels 
  
  
  # Check for dump flag
  elif result.dump:
 
    sqldb = SQLDatabase ( result.host, result.token, result.channel, result.location )
    if ( result.channel is None ):
      sqldb.dumpAllChannels()
    else:
      sqldb.dumpSingleChannel()
  
  # Check for ingest flag
  elif result.ingest:
    
    sqldb = SQLDatabase ( result.host, result.token, result.channel, result.location )
    if ( result.channel is None ):
      sqldb.ingestAllChannels()
    else:
      sqldb.ingestSingleChannel()
    
  else:

      print "Error: Use atleast one option"

if __name__ == "__main__":
  main()

