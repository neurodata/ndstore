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


"""
  Script to write fcollman16. Changes made to chessboard for new OCP names.
"""

import argparse
import cStringIO
import urllib2
import sys
import zlib
import os
import re
from PIL import Image
import MySQLdb
import numpy as np

sys.path += [os.path.abspath('../../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import OCP.ocppaths
import ocpcaproj
import ocpcadb
import zindex
import imagecube

import proteins_collman14 as proteins

class ChessboardIngest:

  def __init__(self, token, resolution, path):

    self.path = path
    self.resolution = resolution

    self.projdb = ocpcaproj.OCPCAProjectsDB()
    self.proj = self.projdb.loadProject ( token )

    (self._ximgsz, self._yimgsz) = self.proj.datasetcfg.imagesz[resolution]
    (self.startslice, self.endslice) = self.proj.datasetcfg.slicerange

    (self.ximagesz, self.yimagesz) = (9888,7936)
    self.batchsz = self.proj.datasetcfg.cubedim[resolution][2]

    self.alldirs = os.listdir ( path )

    # open the database
    self.db = ocpcadb.OCPCADB ( self.proj )

    # get a db cursor 
    self.cursor = self.db.conn.cursor()


  def label ( self, chanid, chanstr ):
    """ Write the channel label/string associated with the channel identifier"""

    sql = 'INSERT INTO channels VALUES ( \'%s\', %s )' % ( chanstr, chanid )
    try:
      print sql
      self.cursor.execute ( sql )
    except MySQLdb.Error, e:
      print ("Error updating channels table: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise 


  def ingest( self ):

    # number the channels
    channel = 0

    # for each protein
    for x in self.alldirs:

      # extract the protein part of the name
      m = re.match('([\d\w]+)',x)
      if m == None:
        continue

      # see if it's a protein
      if m.group(1) in proteins.proteins:

        # ingest each match as a channel
        pdir = x

        # increment the channels starting with 1
        channel+=1


        # label by imaging session and protein, i.e. use the pdir
        self.label ( channel, pdir )
        
# used to count channels
#        continue
         
        # for each slice
        for sl in range(self.startslice,self.endslice+1):

          # New array for every new batch
          if (sl-self.startslice) % self.batchsz == 0:
            imarray = np.zeros ( [self.batchsz,self.yimagesz,self.ximagesz], dtype=np.uint8 )

          # open the slice file and ingest
          #filenm = self.path + '{}/{}_{:0>2}.tif'.format(pdir,pdir,sl)
          filenm = self.path + '{}/{}-{:0>3}_tile-000dcon.tif'.format(pdir,pdir,sl)

          print filenm
          # load the image and check the dimension
          img = Image.open(filenm,'r')
          imgdata = np.asarray(img) 
          # add it to the array
          imarray[(sl-self.startslice)%self.batchsz,:,:] = imgdata
          
          # ingest the batch after reading the last image in batch
          if (sl-self.startslice+1) % self.batchsz == 0:
            self.upload( channel, sl, imarray )

        # ingset any remaining slices
        self.upload( channel, sl, imarray )


  def upload ( self, channel, sl, imarray ):
    """Transfer the array to the database"""

    # get the size of the cube
    xcubedim,ycubedim,zcubedim = self.proj.datasetcfg.cubedim[self.resolution]

    # and the limits of iteration
    xlimit = (self._ximgsz-1) / xcubedim + 1
    ylimit = (self._yimgsz-1) / ycubedim + 1


    for y in range(ylimit):
      for x in range(xlimit):

        # each batch is the last slice in a cube
        z = (sl-self.startslice)/zcubedim

        # zindex
        key = zindex.XYZMorton ( [x,y,z] )

        # Create a channel cube
        cube = imagecube.ImageCube8 ( [xcubedim,ycubedim,zcubedim] )

        # data for this key
        cube.data = imarray[:,y*ycubedim:(y+1)*ycubedim,x*xcubedim:(x+1)*xcubedim]
        # compress the cube
        npz = cube.toNPZ ()

        # add the cube to the database
        sql = "INSERT INTO " + self.proj.getTable(self.resolution) +  "(channel, zindex, cube) VALUES (%s, %s, %s)"
        try:
          self.cursor.execute ( sql, (channel, key, npz))
        except MySQLdb.Error, e:
          print ("Error updating data cube: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
          raise 
    print "Committing at ",x,y,z
    self.db.conn.commit()


def main():

  parser = argparse.ArgumentParser(description='Ingest a tiff stack.')
  parser.add_argument('token', action="store" )
  parser.add_argument('resolution', type=int, action="store" )
  parser.add_argument('path', action="store" )

  result = parser.parse_args()

  cbi = ChessboardIngest( result.token, result.resolution, result.path )
  cbi.ingest()



if __name__ == "__main__":
  main()

