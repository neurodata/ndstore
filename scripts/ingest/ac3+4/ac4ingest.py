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
#  ingest the PNG files into the database
#

"""This file is super-customized for AC4.  Daniels annotations.

     Images in the stack are backward 100 down to 1. 


     Probably the biggest idiosyncracy is the handling of slices.
     They start at 1 and the database aligns slices 1..16, 17..32, etc.
     So, we try to ingest in that pattern.
     
     """

# Stuff we make take from a config or the command line in the future
#  This is the size of amelio's data set
xtilesz = 1024
ytilesz = 1024
_resolution = 1

"""Location of the data

AC4 http://neurodata.io/emca/kasthuri11/hdf5/0/8800,10848/10880,12928/1100,1200/ 

so at res1 first and last image are at 

  http://neurodata.io/emca/kasthuri11/xy/1/4400,5424/5440,6464/1100/
  http://neurodata.io/emca/kasthuri11/xy/1/4400,5424/5440,6464/1199/

"""

startslice = 1100 
endslice = 1199   
batchsz = 20

xoffset = 4400
yoffset = 5440

def main():

  parser = argparse.ArgumentParser(description='Ingest the kasthuri11 dataset annotations.')
  parser.add_argument('baseurl', action="store", help='Base URL to of emca service no http://, e.g. neurodata.io')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('path', action="store", help='Directory with annotation PNG files.')

  result = parser.parse_args()

  # Get a list of the files in the directories
  for sl in range (0,endslice+1-startslice,batchsz):

    newdata = np.zeros ( [ batchsz, ytilesz, xtilesz ], dtype=np.uint32 )
   
    for b in range ( batchsz ):

      if ( sl + b + startslice <= endslice ):

        # For Daniel's backwards slices
        slicenum = endslice - startslice - (sl+b)

        # raw data
        filenm = result.path + '/' + '{:0>4}'.format(slicenum) + '.raw'
        print "Opening filenm" + filenm

        imgdata = np.fromfile ( filenm, dtype=np.uint16 ).reshape([ytilesz,xtilesz])
        newdata[b,:,:]  = imgdata

        # the last z offset that we ingest, if the batch ends before batchsz
        endz = b

    # Now we have a 1024x1024x16 z-aligned cube.  
    #   Send it to the database.
    url = 'http://%s/emca/%s/npdense/%s/%s,%s/%s,%s/%s,%s/' % ( result.baseurl, result.token, _resolution, xoffset, xoffset+xtilesz, yoffset, yoffset+ytilesz, startslice+sl, startslice+sl+endz+1)

    print url

    # Encode the voxelist an pickle
    fileobj = cStringIO.StringIO ()
    np.save ( fileobj, newdata )

    cdz = zlib.compress (fileobj.getvalue())

    # Build the post request
    try:
      req = urllib2.Request(url, cdz)
      response = urllib2.urlopen(req)
      the_page = response.read()
    except Exception, e:
      print "Failed ", e

if __name__ == "__main__":
  main()

