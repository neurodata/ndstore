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

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import imagecube
import ndlib
import ocpcarest
import ocpcaproj
import ocpcadb

  
def ingest ( token, resolution ):
    """ Read the stack and ingest """

    with closing ( ocpcaproj.OCPCAProjectsDB() ) as projdb:
      proj = projdb.loadProject ( token )

    with closing ( ocpcadb.OCPCADB (proj) ) as db:

      (xcubedim, ycubedim, zcubedim) = cubedims = proj.datasetcfg.cubedim[resolution]

      zidx = 0
      cube = imagecube.ImageCube16 ( cubedims )
      cube.zeros()
      cube.data = np.array(range(xcubedim*ycubedim*zcubedim), dtype=np.uint8).reshape(cubedims)
      db.putCube ( zidx, resolution, cube )
      db.conn.commit()
      c = db.getCube ( zidx, resolution )
      print c.data
      cube2 = imagecube.ImageCube16 ( cubedims )
      cube2.data = np.zeros( cubedims, dtype=np.uint8 )
      db.putCube ( zidx, resolution, cube2, True )
      db.conn.commit()
      c = db.getCube ( zidx, resolution )
      import pdb; pdb.set_trace()
      print c.data


def main():

  parser = argparse.ArgumentParser(description='Ingest a CATMAID stack')
  parser.add_argument('token', action="store")
  parser.add_argument('resolution', action="store", type=int)

  result = parser.parse_args()
  ingest(result.token, result.resolution)


if __name__ == "__main__":
  main()

