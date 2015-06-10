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
import sys
import os
import numpy as np
from contextlib import closing
from PIL import Image
import zlib

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import ocpcaproj
import ocpcadb
import ocplib
import imagecube

"""Construct an image hierarchy up from a given resolution"""

class OCPCAStack:
  """ Stack of images """

  def __init__ ( self, token):
    """ Load the database and project """

    with closing ( ocpcaproj.OCPCAProjectsDB() ) as projdb:
      proj = projdb.loadProject ( token )

      if proj.getDBType() in ocpcaproj.TIMESERIES_DATASETS:
        self.build_TSStack ( token )
      elif proj.getDBType() in ocpcaproj.IMAGE_DATASETS:
        self.build_ImageStack ( token )

  def build_TSStack ( self, token ):
    """Build the hierarchy of images"""

    with closing ( ocpcaproj.OCPCAProjectsDB() ) as projdb:
      proj = projdb.loadProject ( token )

    with closing ( ocpcadb.OCPCADB (proj) ) as db:

      for resolution in range ( proj.datasetcfg.resolutions[1], len(proj.datasetcfg.resolutions) ):

        # Get the source database sizes
        [ximagesz, yimagesz] = proj.datasetcfg.imagesz [ resolution ]
        [xcubedim, ycubedim, zcubedim] = cubedims = proj.datasetcfg.cubedim [ resolution ]

        # Get the slices
        [ startslice, endslice ] = proj.datasetcfg.slicerange
        slices = endslice - startslice + 1
        [ starttime, endtime ] = proj.datasetcfg.timerange

        # Set the limits for iteration on the number of cubes in each dimension
        # RBTODO These limits may be wrong for even (see channelingest.py)
        xlimit = ximagesz - 1 / xcubedim + 1
        ylimit = yimagesz - 1  / ycubedim + 1
        #  Round up the zlimit to the next larger
        zlimit = (((slices-1)/zcubedim+1)*zcubedim)/zcubedim 

        for t in range( starttime, endtime+1, 1): 
          for z in range(zlimit):
            for y in range(ylimit):
              for x in range(xlimit):

                key = ocplib.XYZMorton ( [x,y,z] )
                print key,t
                continue
                #key2 = ocplib.XYZMorton ( [x+1,y+1,z] )
                # cutout the data at the -1 resolution
                #olddata1 = db.getTimeSeriesCube( key, t, resolution-1 ).data
                #olddata2 = db.getTimeSeriesCube( key, t, resolution-1 ).data
                olddata = db.cutout ( [ x*2*xcubedim, y*2*ycubedim, z*zcubedim ], [xcubedim*2,ycubedim*2,zcubedim], resolution-1, t ).data

                # target array for the new data (z,y,x) order
                newdata = np.zeros ( cubedims[::-1], dtype=olddata.dtype )

                for sl in range(zcubedim):

                  # Convert each slice to an image
                  if proj.getDBType() in ocpcaproj.DATASETS_16bit:
                    slimage = Image.frombuffer ( 'I;16', (xcubedim*2,ycubedim*2), olddata[sl,:,:].flatten(), 'raw', 'I;16', 0, 1 )
                  elif proj.getDBType() in ocpcaproj.DATATSETS_8bit:
                    slimage = Image.frombuffer ( 'L', (xcubedim*2,ycubedim*2), olddata[sl,:,:].flatten(), 'raw', 'L', 0, 1 )

                  # Resize the image and Put to a new cube
                  newdata[sl,:,:] = np.asarray ( slimage.resize( [xcubedim,ycubedim] ) )

                if proj.getDBType() == ocpcaproj.TIMESERIES_4d_8bit:
                  newcube = imagecube.ImageCube8 ( cubedims )
                elif proj.getDBType() == ocpcaproj.TIMESERIES_4d_16bit:
                  newcube = imagecube.ImageCube16 ( cubedims )
                
                newcube.data = newdata
                # put in the database
                db.putTimeSeriesCube( key, t, resolution, newcube )

          db.conn.commit()


  def build_ImageStack ( self, token ):
    """Build the hierarchy of images"""

    with closing ( ocpcaproj.OCPCAProjectsDB() ) as projdb:
      proj = projdb.loadProject ( token )

    with closing ( ocpcadb.OCPCADB (proj) ) as db:

      for resolution in range ( proj.datasetcfg.resolutions[1], len(proj.datasetcfg.resolutions) ):

        # Get the source database sizes
        [ximagesz, yimagesz] = proj.datasetcfg.imagesz [ resolution ]
        [xcubedim, ycubedim, zcubedim] = cubedims = proj.datasetcfg.cubedim [ resolution ]

        # Get the slices
        [ startslice, endslice ] = proj.datasetcfg.slicerange
        slices = endslice - startslice + 1
        [ starttime, endtime ] = proj.datasetcfg.timerange

        # Set the limits for iteration on the number of cubes in each dimension
        # RBTODO These limits may be wrong for even (see channelingest.py)
        xlimit = ximagesz - 1 / xcubedim + 1
        ylimit = yimagesz - 1  / ycubedim + 1
        #  Round up the zlimit to the next larger
        zlimit = (((slices-1)/zcubedim+1)*zcubedim)/zcubedim 

        for z in range(zlimit):
          for y in range(ylimit):
            for x in range(xlimit):

              key = ocplib.XYZMorton ( [x,y,z] )
              olddata = db.cutout ( [ x*2*xcubedim, y*2*ycubedim, z*zcubedim ], [xcubedim*2,ycubedim*2,zcubedim], resolution-1, t ).data

              # target array for the new data (z,y,x) order
              newdata = np.zeros ( cubedims[::-1], dtype=olddata.dtype )

              for sl in range(zcubedim):
                
                # Convert each slice to an image
                # Convert each slice to an image
                if proj.getDBType() in ocpcaproj.DATASETS_16bit:
                  slimage = Image.frombuffer ( 'I;16', (xcubedim*2,ycubedim*2), olddata[sl,:,:].flatten(), 'raw', 'I;16', 0, 1 )
                elif proj.getDBType() in ocpcaproj.DATATSETS_8bit:
                  slimage = Image.frombuffer ( 'L', (xcubedim*2,ycubedim*2), olddata[sl,:,:].flatten(), 'raw', 'L', 0, 1 )

                # Resize the image and Put to a new cube
                newdata[sl,:,:] = np.asarray ( slimage.resize( [xcubedim,ycubedim] ) )

              if proj.getDBType() in ocpcaproj.DATATSETS_8bit:
                newcube = imagecube.ImageCube8 ( cubedims )
              elif proj.getDBType() == ocpcaproj.DATASETS_16bit:
                newcube = imagecube.ImageCube16 ( cubedims )
              
              newcube.data = newdata
              # put in the database
              db.putCube( key, resolution, newcube )

        db.conn.commit()


def main():

  parser = argparse.ArgumentParser(description='Build an OCP stack')
  parser.add_argument('token', action="store", help='Token for the project.')
  parser.add_argument('resolution', action="store", type=int, help='Start (highest) resolution to build')
  
  result = parser.parse_args()

  # Create the annotation stack
  ocpcastack = OCPCAStack ( result.token )


if __name__ == "__main__":
  main()

