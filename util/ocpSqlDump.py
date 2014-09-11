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

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import ocpcaproj
import ocpcadb

class SQLDatabase:

  def __init__(self, password, host, token, location):
    """ Load the database and project """

    self.projdb = ocpcaproj.OCPCAProjectsDB()
    self.proj = self.projdb.loadProject ( token )
    self.imgDB = ocpcadb.OCPCADB ( self.proj )
    self.password = password
    self.host = host
    self.token = token
    self.location = location
    self.starterString = '-u brain -p{} -h {}'.format( self.password, self.host )

  def dumpImgStack( self ):
    """ Dump an Image Stack """

    for i in range( 0, len(self.proj.datasetcfg.resolutions ) ):

      cmd = 'mysqldump {} {} --tables res{} > {}{}.res{}.sql'.format ( self.starterString, self.token, i, self.location, self.token, i )
      print cmd
      os.system ( cmd )


  def dumpAnnotationStack( self ):
    """ Dump an Annotation Stack """

    cmd = 'mysqldump {} {} > {}{}.sql'.format ( self.starterString, self.token, self.location, self.token )
    print cmd
    os.system ( cmd )

  
  def dumpChannelStack( self ):
    """ Dump a Channel Stack """

    cmd = 'mysqldump {} {} --tables {} > {}{}.{}.sql'.format ( self.starterString, self.token, 'channels', self.location, self.token, 'channels' )
    print cmd
    os.system( cmd )
    self.dumpImgStack()


  def ingestImageStack ( self ):
    """ Ingest an Image Stack """

    for i in range(0, len(self.proj.datasetcfg.resolutions ) ):
      
      cmd = 'mysql () {} < {}{}.res{}.sql'.format ( self.starterString, self.token, self.location, self.token, i )
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
  parser.add_argument('password', action="store", help='SQL Database Password')
  parser.add_argument('token', action="store", help='Token for the project.')
  parser.add_argument('location', action="store", help='Location where to store the dump[')
  parser.add_argument('--dump', dest='dump', action="store_true", help='Dump the database into a sqldump')
  parser.add_argument('--ingest', dest='ingest', action="store_true", help='Ingest the sqldump')
  parser.add_argument('--dbcopy', dest='dbcopy', action="store", default=None, help='Ingest the sqldump')

  result = parser.parse_args()

  sqldb = SQLDatabase( result.password, result.host, result.token, result.location )

  # Check for copy flag
  if result.dbcopy!=None:
    

    if ( sqldb.proj.getDBType() == ocpcaproj.IMAGES_8bit or sqldb.proj.getDBType() == ocpcaproj.IMAGES_16bit or sqldb.proj.getDBType() == ocpcaproj.RGB_32bit or sqldb.proj.getDBType() == ocpcaproj.RGB_64bit ):
        
      sqldb = SQLDatabase( result.password, result.host, result.token, result.location )
      sqldb.dumpImgStack()
      sqldb = SQLDatabase( result.password, result.host, result.dbcopy, result.location )
      sqldb.ingestImageStack()
  
    elif ( sqldb.proj.getDBType() == ocpcaproj.CHANNELS_8bit or sqldb.proj.getDBType() == ocpcaproj.CHANNELS_16bit ):

      sqldb.dumpChannelStack()
      sqldb.ingestChannelStack()
  
  # Check for dump flag
  elif result.dump:
 
    sqldb = SQLDatabase( result.password, result.host, result.token, result.location )

    if ( sqldb.proj.getDBType() == ocpcaproj.IMAGES_8bit or sqldb.proj.getDBType() == ocpcaproj.IMAGES_16bit or sqldb.proj.getDBType() == ocpcaproj.RGB_32bit or sqldb.proj.getDBType() == ocpcaproj.RGB_64bit ):
      
      sqldb.dumpImgStack()
    
    elif ( sqldb.proj.getDBType() == ocpcaproj.CHANNELS_8bit or sqldb.proj.getDBType() == ocpcaproj.CHANNELS_16bit ):

      sqldb.dumpChannelStack()

    else:
      
      sqldb.dumpAnnotationStack()
  
  # Check for ingest flag
  elif result.ingest:
    
    sqldb = SQLDatabase( result.password, result.host, result.token, result.location )
    
    if ( sqldb.proj.getDBType() == ocpcaproj.IMAGES_8bit or sqldb.proj.getDBType() == ocpcaproj.IMAGES_16bit or sqldb.proj.getDBType() == ocpcaproj.RGB_32bit or sqldb.proj.getDBType() == ocpcaproj.RGB_64bit ):
      
      sqldb.ingestImageStack()
    
    elif ( sqldb.proj.getDBType() == ocpcaproj.CHANNELS_8bit or sqldb.proj.getDBType() == ocpcaproj.CHANNELS_16bit ):

      sqldb.ingestChannelStack()
    
    else:
      
      sqldb.ingestAnnotataionStack()

  else:

      print "Error: Use atleast one option"

if __name__ == "__main__":
  main()

