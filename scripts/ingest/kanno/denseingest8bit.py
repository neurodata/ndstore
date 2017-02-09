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
import sys
import os

import numpy as np
from PIL import Image
import urllib, urllib2
import cStringIO
import collections
import zlib

import kanno_cy

#
#  This is for VAST exports that are 8-bit.
#

"""This file is super-customized for the kasthuri annotations data.
     Probably the biggest idiosyncracy is the handling of slices.
     They start at 1 and the database aligns slices 1..16, 17..32, etc.
     So, we try to ingest in that pattern."""

# Stuff we make take from a config or the command line in the future
_xtilesz = 10748
_ytilesz = 12896
_startslice = 1840 
_endslice = 1849
_prefix = 'Threecylinders_Synapses_forJHU_export_s'
#_batchsz = 16 
_batchsz = 16 

# Shape that we want to ingest into the database.
#  This should be aligned to the database cube size to perform best.
_zingestsz = 16
_yingestsz = 1024
_xingestsz = 1024


def main():

  parser = argparse.ArgumentParser(description='Ingest the kasthuri11 dataset annotations.')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('resolution', action="store", help='Resolution of the ingest data.')
  parser.add_argument('path', action="store", help='Directory with annotation PNG files.')
  
  result = parser.parse_args()

  # Get a list of the files in the directories
  for sl in range (_startslice,_endslice+1,_batchsz):

        # force the collection of the previous array.
        newdata = None                   
        data = None
        import gc
        gc.collect()

        newdata = np.zeros ( [ _batchsz, _ytilesz, _xtilesz ], dtype=np.uint32 )
        for b in range ( _batchsz ):
          if ( sl + b <= _endslice ):

            filenm = result.path + '/' + _prefix + '{:0>4}'.format(sl+b) + '.png'
            print filenm
            tileimage = Image.open ( filenm, 'r' )
            imgdata = np.asarray ( tileimage )

            newdata[b,:,:] = imgdata
            print np.unique(imgdata)

            # the last z offset that we ingest, if the batch ends before _batchsz
            endz = b
    
        zlow = sl+1
        zhigh = sl+endz+2
        ylow = 0
        yhigh = _ytilesz
        xlow = 0
        xhigh = _xtilesz

        # Send a cube at a time to the database
        for z in range ( zlow, zhigh, _zingestsz ):
          for y in range ( ylow, yhigh, _yingestsz ):
            for x in range ( xlow, xhigh, _xingestsz ):
              
              # cutout the data
              data = newdata[ z-zlow:min(zhigh,z+_zingestsz)-zlow,\
                              y-ylow:min(yhigh,y+_yingestsz)-ylow,\
                              x-xlow:min(xhigh,x+_xingestsz)-xlow]

              # check if there's anything to store
              if ( np.count_nonzero(data) != 0 ):

                url = 'http://localhost/ocp/ca/%s/npz/%s/%s,%s/%s,%s/%s,%s/' % ( result.token, result.resolution, x, min(xhigh,x+_xingestsz), y, min(yhigh,y+_yingestsz), z, min(zhigh,z+_zingestsz ))

                print url

                # Encode the voxelist an pickle
                fileobj = cStringIO.StringIO ()
                np.save ( fileobj, data )

                cdz = zlib.compress (fileobj.getvalue())

                # Build the post request
                req = urllib2.Request(url, cdz)
                response = urllib2.urlopen(req)
                the_page = response.read()

        


if __name__ == "__main__":
  main()

