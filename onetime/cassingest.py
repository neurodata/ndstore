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
import h5py
import tempfile
import urllib, urllib2
import cStringIO
from PIL import Image
import zlib
import MySQLdb
from cassandra.cluster import Cluster

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import ocpcaproj
import ocpcadb
import zindex

"""Construct an image hierarchy up from a given resolution"""

def main():

  parser = argparse.ArgumentParser(description='Build an aeropsike DB from mysql data.')
  parser.add_argument('token', action="store", help='Token for the project.')
  parser.add_argument('resolution', action="store", type=int)
  
  result = parser.parse_args()

  # as database
  cluster = Cluster()
  session = cluster.connect(result.token)

  # mysql database
  projdb = ocpcaproj.OCPCAProjectsDB()
  proj = projdb.loadProject ( result.token )

  # Bind the annotation database
  imgDB = ocpcadb.OCPCADB ( proj )

  # Get the source database sizes
  [ximagesz, yimagesz] = proj.datasetcfg.imagesz [ result.resolution ]
  [xcubedim, ycubedim, zcubedim] = cubedim = proj.datasetcfg.cubedim [ result.resolution ]

  # Get the slices
  [ startslice, endslice ] = proj.datasetcfg.slicerange
  slices = endslice - startslice + 1

  # Set the limits for iteration on the number of cubes in each dimension
  # RBTODO These limits may be wrong for even (see channelingest.py)
  xlimit = ximagesz / xcubedim
  ylimit = yimagesz / ycubedim
  #  Round up the zlimit to the next larger
  zlimit = (((slices-1)/zcubedim+1)*zcubedim)/zcubedim 

  cursor = imgDB.conn.cursor()

  import pdb; pdb.set_trace()

  for z in range(zlimit):
    for y in range(ylimit):
      for x in range(xlimit):

#        mysqlcube = imgDB.cutout ( [ x*xcubedim, y*ycubedim, z*zcubedim ], cubedim, result.resolution )
        zidx = zindex.XYZMorton ( [x,y,z] )
        cube = imgDB.getCube ( zidx, result.resolution, zidx )
        imgDB.cputCube ( zidx, result.resolution, cube )
        print "Ingesting {}".format(zidx)
#
#       tmpfiletocass = tempfile.NamedTemporaryFile ()
#       h5tocass = h5py.File ( tmpfiletocass.name ) 
#       h5tocass.create_dataset ( "cuboid", tuple(mysqlcube.data.shape), mysqlcube.data.dtype,
#                                compression='gzip',  data=mysqlcube.data )
#       h5tocass.close()
#       tmpfiletocass.seek(0)
#       
#       cql = "INSERT INTO cuboids ( resolution, zidx, cuboid ) VALUES ( %s, %s, %s )"
#       session.execute ( cql, ( result.resolution, zidx, tmpfiletocass.read().encode('hex')))
#
#        cql = "SELECT cuboid FROM cuboids WHERE resolution = %s AND zidx = %s"
#        row = session.execute ( cql, ( result.resolution, zidx ))
## RB verify that the data is there.
#        tmpfilefromcass = tempfile.NamedTemporaryFile ()
#        tmpfilefromcass.write ( row[0].cuboid.decode('hex') )
#        tmpfilefromcass.seek(0)
#        h5fromcass = h5py.File ( tmpfilefromcass.name ) 



if __name__ == "__main__":
  main()

