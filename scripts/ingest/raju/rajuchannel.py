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

import argparse
import cStringIO
import urllib2
import sys
import zlib
import os
import re
from PIL import Image
import cv2
from contextlib import closing
import numpy as np

sys.path += [os.path.abspath('../../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import ocpcarest
import ndlib
import imagecube
import ocpcadb
import ocpcaproj

class RajuIngest:

  def __init__(self, token, path, resolution, channel):

    self.token = token
    self.path = path
    self.resolution = resolution

    with closing ( ocpcaproj.OCPCAProjectsDB() ) as self.projdb:
      self.proj = self.projdb.loadProject ( token )

    with closing ( ocpcadb.OCPCADB(self.proj) ) as self.db:

      (self.xcubedim, self.ycubedim, self.zcubedim) = self.cubedims = self.proj.datasetcfg.cubedim[ resolution ]
      (self.startslice, self.endslice) = self.proj.datasetcfg.slicerange
      self.batchsz = self.zcubedim
      
      self.channel = channel

      (self._ximgsz,self._yimgsz) = self.proj.datasetcfg.imagesz[resolution]


  def label ( self, chanid, chanstr ):
    """ Write the channel label/string associated with the channel identifier"""

    with closing ( ocpcadb.OCPCADB(self.proj) ) as self.db:
      self.db.putChannel ( chanstr, chanid )

  def ingest( self ):

    NAME = [ "Grayscale" ]

    # for each channel
    for x in range(self.channel):
     
      # label by RGB Channel
      self.label ( x+1, NAME[x] )

      # for each slice
      for sl in range(self.startslice , self.endslice+1, self.batchsz):
      
        imarray = np.zeros ( [self.batchsz,self._yimgsz,self._ximgsz], dtype=np.uint16 )

        for b in range ( self.batchsz ):

          if ( sl + b < self.endslice ):

            # raw data
            #filenm = '{}{}_{:0>4}.tif'.format(self.path, self.token.strip('Affine'), sl+b)
            filenm = '{}allenAtlasPadded{:0>4}.tif'.format(self.path,  sl+b)

            # load the image and check the dimension
            try:
              print "Opening filename: " + filenm
              imgdata = cv2.imread(filenm, -1)
              #img = Image.open(filenm, 'r')
              #imgdata = np.asarray ( img )
              #if imgdata == None:
              #    imgdata = np.zeros((self._yimgsz,self._ximgsz))
              imarray[(sl+b-self.startslice)%self.batchsz,0:imgdata.shape[0],0:imgdata.shape[1]] = imgdata
            except IOError, e:
              print e
          
        # ingset any remaining slices
        self.upload( x+1, sl, imarray )


  def upload ( self, channel, sl, imarray ):
    """Transfer the array to the database"""

    with closing ( ocpcadb.OCPCADB(self.proj) ) as self.db:
      
      for y in range ( 0 , self._yimgsz+1, self.ycubedim ):
        for x in range ( 0, self._ximgsz+1, self.xcubedim ):

          # zindex
          key = ndlib.XYZMorton ( [x/self.xcubedim, y/self.ycubedim, (sl-self.startslice)/self.zcubedim] )

          # Create a channel cube
          cube = imagecube.ImageCube16 ( self.cubedims )
          
          xmin = x
          ymin = y
          xmax = min ( self._ximgsz, x + self.xcubedim )
          ymax = min ( self._yimgsz, y + self.ycubedim )
          zmin = 0
          zmax = min ( sl + self.zcubedim, self.endslice + 1 )

          # data for this key
          cube.data[0:zmax-zmin,0:ymax-ymin,0:xmax-xmin] = imarray[zmin:zmax,ymin:ymax, xmin:xmax]
          print cube.data.shape
          #import pdb;pdb.set_trace()
          self.db.putChannelCube(key, channel, self.resolution, cube)
      
        print " Commiting at x={}, y={}, z={}".format(x, y, sl)
        self.db.conn.commit()


def main():

  parser = argparse.ArgumentParser(description='Ingest a multi-channel tiff stack.')
  parser.add_argument('token', action="store", help='Token for the project' )
  parser.add_argument('resolution', type=int, action="store", help='Resolution of data' )
  parser.add_argument('channel', type=int, action="store", help='Number of Channels' )
  parser.add_argument('path', action="store", help='Directory for the image files' )

  result = parser.parse_args()

  raj = RajuIngest( result.token, result.path, result.resolution, result.channel )
  raj.ingest()


if __name__ == "__main__":
  main()

