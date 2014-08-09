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

import argparse
import cStringIO
import urllib2
import sys
import zlib
import os
import re
#from PIL import Image
import cv2
import Image
import MySQLdb

import numpy as np

sys.path += [os.path.abspath('../../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import ocpcarest
import zindex
import imagecube

class MitraIngest:

  def __init__(self, token, path, resolution, channel):

    self.path = path
    self.resolution = resolution

    [ self.db, self.proj, self.projdb ] = ocpcarest.loadDBProj ( token )

    (self.xcubedim, self.ycubedim, self.zcubedim) = self.proj.datasetcfg.cubedim[ resolution ]
    (self.startslice, self.endslice) = self.proj.datasetcfg.slicerange
    self.batchsz = self.zcubedim
    
    self.channel = channel

    self._ximgsz = self.proj.datasetcfg.imagesz[resolution][0]
    self._yimgsz = self.proj.datasetcfg.imagesz[resolution][1]

    self.cursor = self.db.conn.cursor()


  def label ( self, chanid, chanstr ):
    """ Write the channel label/string associated with the channel identifier"""

    sql = 'INSERT INTO channels VALUES ( \'{}\', {} )'.format( chanstr, chanid )
    try:
      print sql
      #self.cursor.execute ( sql )
    except MySQLdb.Error, e:
      print ("Error updating channels table: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise 


  def ingest( self ):

    channel = 0
    NAME = [ "Red", "Green", "Blue" ]
    import pdb; pdb.set_trace()

    # for each channel
    for x in range(self.channel):
      
      # label by RGB Channel
      self.label ( x, NAME[x] )
         
      # for each slice
      for sl in range(self.startslice,self.endslice+1,self.batchsz):
      
        imarray = np.zeros ( [self.batchsz,self._yimgsz,self._ximgsz], dtype=np.uint8 )

        for b in range ( self.batchsz ):

          if ( sl + b <= self.endslice ):

            # raw data
            filenm = self.path + '{:0>4}'.format(sl+b) + '.tiff'

            # load the image and check the dimension
            try:
              print "Opening filename: " + filenm
              img = Image.open(filenm, 'r')
              imgdata = np.asarray ( img )
              imarray[(sl+b-self.startslice)%self.batchsz,0:imgdata.shape[0],0:imgdata.shape[1]] = imgdata[:,:,x]
            except IOError, e:
              print e
          
        # ingset any remaining slices
        self.upload( channel, sl, imarray )


  def upload ( self, channel, sl, imarray ):
    """Transfer the array to the database"""

    # and the limits of iteration
    xlimit = (self._ximgsz-1) / self.xcubedim + 1
    ylimit = (self._yimgsz-1) / self.ycubedim + 1

    for y in range(ylimit):
      for x in range(xlimit):

        # each batch is the last slice in a cube
        z = sl/self.zcubedim

        # zindex
        key = zindex.XYZMorton ( [x,y,z] )

        # Create a channel cube
        cube = imagecube.ImageCube8 ( [self.xcubedim, self.ycubedim, self.zcubedim] )

        # data for this key
        cube.data = imarray[:,y*self.ycubedim:(y+1)*self.ycubedim,x*self.xcubedim:(x+1)*self.xcubedim]
        # compress the cube
        npz = cube.toNPZ ()

        # add the cube to the database
        sql = "INSERT INTO " + self.proj.getTable(self.resolution) +  "(channel, zindex, cube) VALUES (%s, %s, %s)"
        try:
          print sql
          #self.cursor.execute ( sql, (channel, key, npz))
        except MySQLdb.Error, e:
          print ("Error updating data cube: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
          raise 

    self.db.conn.commit()


def main():

  parser = argparse.ArgumentParser(description='Ingest a multi-channel tiff stack.')
  parser.add_argument('token', action="store", help='Token for the project' )
  parser.add_argument('path', action="store", help='Directory for the image files' )
  parser.add_argument('resolution', type=int, action="store", help='Resolution of data' )
  parser.add_argument('channel', type=int, action="store", help='Number of Channels' )

  result = parser.parse_args()

  mit = MitraIngest( result.token, result.path, result.resolution, result.channel )
  mit.ingest()


if __name__ == "__main__":
  main()

