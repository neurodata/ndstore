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
import argparse
import cStringIO
import numpy as np
from PIL import Image
import zlib
from contextlib import closing


sys.path += [os.path.abspath('../../django')]
import OCP.settings
#settings.configure()
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings
import django
django.setup()

import imagecube
import ocplib
import ocpcarest
import ocpcaproj
import ocpcadb
from cube import Cube

class NikhilIngest:

  def __init__(self, path, resolution, token_name, channel_name):
    print "In initialization"
    """ Load image stack into OCP, creating tokens and channels as needed """

    self.token = token_name
    self.resolution = resolution
    self.path = path

    with closing (ocpcaproj.OCPCAProjectsDB()) as projdb:
      self.proj = projdb.loadToken(self.token)
      self.channel_name = channel_name
      self.ingest()

  def ingest(self):
    """ Read image stack and ingest """

    # Load a database
    with closing(ocpcaproj.OCPCAProjectsDB()) as projdb:
      proj = projdb.loadToken(self.token)

    with closing(ocpcadb.OCPCADB(proj)) as db:

      ch = proj.getChannelObj(self.channel_name)
      # get the dataset configuration
      [[ximagesz, yimagesz, zimagesz], (starttime, endtime)] = proj.datasetcfg.imageSize(self.resolution)
      [xcubedim, ycubedim, zcubedim] = cubedim = proj.datasetcfg.getCubeDims()[self.resolution]
      [xoffset, yoffset, zoffset] = proj.datasetcfg.getOffset()[self.resolution]

      # Get a list of the files in the directories
      
      for slice_number in range(zoffset, zimagesz, zcubedim):
        slab = np.zeros([zcubedim, yimagesz, ximagesz], dtype=np.uint32)

        for b in range(zcubedim):
          file_name = "{}{}{:0>4}.tif".format(self.path, self.token, slice_number+b)
          print "Open filename {}".format(file_name)

          try:
            img = Image.open(file_name,'r')
            slab [b,:,:] = np.asarray(img)
          except IOError, e:
            print "Failed to open file %s" % (e)
            img = np.zeros((yimagesz,ximagesz), dtype=np.uint8)
            slab [b,:,:] = img

        for y in range(0, yimagesz + 1, ycubedim):
          for x in range(0, ximagesz + 1, xcubedim):

            # Getting a Cube id and ingesting the data one cube at a time
            zidx = ocplib.XYZMorton([x / xcubedim, y / ycubedim, (slice_number - zoffset) / zcubedim])
            cube = Cube.getCube(cubedim, ch.getChannelType(), ch.getDataType())
            cube.zeros()

            xmin = x
            ymin = y
            xmax = min(ximagesz, x + xcubedim)
            ymax = min(yimagesz, y + ycubedim)
            zmin = 0
            zmax = min(slice_number + zcubedim, zimagesz + 1)

            cube.data[0:zmax - zmin, 0:ymax - ymin, 0:xmax - xmin] = slab[zmin:zmax, ymin:ymax, xmin:xmax]
            from operator import sub
            corner = map(sub, [x,y,slice_number], [xoffset,yoffset,zoffset])
            if cube.data.any():
              db.annotateDense ( ch, corner, self.resolution, cube.data, 'O' )
            


def main():

  parser = argparse.ArgumentParser(description='Ingest a OCP stack')
  parser.add_argument('token', action="store")
  parser.add_argument('resolution', action="store", type=int)
  parser.add_argument('path', action="store")
  parser.add_argument('channel_name', action="store")

  result = parser.parse_args()

  ni = NikhilIngest (result.path, result.resolution, result.token, result.channel_name)
  ni.ingest()

if __name__ == "__main__":
  main()
