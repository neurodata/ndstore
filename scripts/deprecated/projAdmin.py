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

import os
import sys
import argparse
import MySQLdb

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import ocpcaproj
import ocpcaprivate


class Dataset():
  
  def __init__(self, inputData):
    """ Load the dataset info """

    ( self.ximagesize, self.yimagesize, self.startslice, self.endslice, self.zoomlevels, self.zscale, self.startwindow, self.endwindow, self.starttime, self.endtime ) = inputData

class Project():

  def __init__(self, inputData):
    """ Load the project info """

    ( self.token, self.openid, self.dbhost, self.project, self.dbtype, self.dataset, self.dataurl, self.readonly, self.exceptions, self.resolution, self.public, self.kvengine, self.kvserver, self.propagate ) = inputData


class OCPAdmin ():

  def __init__(self, host, remotehost, token, dataset ):
    """ Load the Project Info """
    
    self.token = token
    self.dataset = dataset
    self.conn = MySQLdb.connect( host=host, user=ocpcaprivate.dbuser, passwd=ocpcaprivate.dbpasswd, db=ocpcaprivate.db )
    self.remoteconn = MySQLdb.connect( host=remotehost, user=ocpcaprivate.dbuser, passwd=ocpcaprivate.dbpasswd, db=ocpcaprivate.db )


  def loadProject ( self ):
    """ Load a Project Information from the database """

    sql = "SELECT token, openid, host, project, datatype, dataset, dataurl, readonly, exceptions, resolution, public, kvengine, kvserver, propagate from %s where token = \'%s\'" % (ocpcaprivate.projects, self.token)

    try:
      cursor = self.conn.cursor()
      cursor.execute( sql )
    except MySQLdb.Error, e:
      print e

    row = cursor.fetchone()

    if ( row==None ):
      raise Exception ( "Project {} not found".format( self.token ) )

    return row

  
  def insertProject ( self ):
    """ Insert a Project Information to a remote database """

    proj = Project ( self.loadProject() )
    sql = "INSERT INTO {0} (token, openid, host, project, datatype, dataset, dataurl, readonly, exceptions, resolution, public, kvengine, kvserver, propagate) VALUES (\'{1}\',\'{2}\',\'{3}\',\'{4}\',{5},\'{6}\',\'{7}\',\'{8}\',\'{9}\',\'{10}\',\'{11}\',\'{12}\',\'{13}\',\'{14}\')".format (ocpcaprivate.projects, self.token, proj.openid, proj.dbhost, proj.project, proj.dbtype, proj.dataset, proj.dataurl, proj.readonly, proj.exceptions, proj.resolution, proj.public, proj.kvengine, proj.kvserver, proj.propagate )

    try:
      cursor = self.remoteconn.cursor()
      cursor.execute( sql )
      self.remoteconn.commit()
    except MySQLdb.Error, e:
      print e

  
  def loadDataset ( self ):
    """ Load a Dataset Information from the database """

    sql = "SELECT ximagesize, yimagesize, startslice, endslice, zoomlevels, zscale, startwindow, endwindow, starttime, endtime from %s where dataset = \'%s\'" % (ocpcaprivate.datasets, self.dataset)
    
    try:
      cursor = self.conn.cursor()
      cursor.execute( sql )
    except MySQLdb.Error, e:
      print e

    row = cursor.fetchone()

    if ( row==None ):
      raise Exception ( "Project {} not found".format(self.dataset) )

    return row

  
  def insertDataset ( self ):
    """ Insert a Dataset Information into a remote database """

    dat = Dataset ( self.loadDataset() )

    sql = "INSERT INTO {0} (dataset, ximagesize, yimagesize, startslice, endslice, zoomlevels, zscale, startwindow, endwindow, starttime, endtime) VALUES (\'{1}\',\'{2}\',\'{3}\',\'{4}\',{5},\'{6}\',\'{7}\',\'{8}\',\'{9}\',\'{10}\',\'{11}\')".format ( ocpcaprivate.datasets, self.dataset, dat.ximagesize, dat.yimagesize, dat.startslice, dat.endslice, dat.zoomlevels, dat.zscale, dat.startwindow, dat.endwindow, dat.starttime, dat.endtime )

    try:
      cursor = self.remoteconn.cursor()
      cursor.execute( sql )
      self.remoteconn.commit()
    except MySQLdb.Error, e:
      print e


def main():

  parser = argparse.ArgumentParser ( description="Enter admin info from command line")
  parser.add_argument('host', action="store", help='Hostname where to copy from')
  parser.add_argument('token', action="store", help='Token')
  parser.add_argument('dataset', action="store", help='Dataset')
  parser.add_argument('remotehost', action="store", help='Remote Hostname where to copy to')
  parser.add_argument('--project', dest="proj", action="store_true", help='Copy only project')
  parser.add_argument('--dataset', dest="dst", action="store_true", help='Copy only dataset')

  result = parser.parse_args()

  ocpadmin = OCPAdmin(result.host, result.remotehost, result.token, result.dataset )
  if ( result.proj ):
    ocpadmin.insertProject()
  elif ( result.dst ):
    ocpadmin.insertDataset()
  else:
    ocpadmin.insertDataset()
    ocpadmin.insertProject()


if __name__ == "__main__":
  main()
