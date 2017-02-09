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
from scipy.misc import imresize
from scipy.misc import imread
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
xtilesz = 67840
#xtilesz = 512
ytilesz = 59904
#ytilesz = 512

_resolution = 1

"""Location of the data

  http://neurodata.io/emca/kasthuri11/hdf5/0/10944,12992/17424,19472/1000,1256/

so at res1 first and last image are at 

  http://neurodata.io/emca/kasthuri11/xy/1/5472,6496/8712,9736/1000/
  http://neurodata.io/emca/kasthuri11/xy/1/5472,6496/8712,9736/1255/

"""
ss = 2916
startslice = 6 
endslice = 9   
batchsz = 16

xoffset = 0
yoffset = 0

def main():

  parser = argparse.ArgumentParser(description='Ingest the kasthuri11 dataset annotations.')
  parser.add_argument('baseurl', action="store", help='Base URL to of emca service no http://, e.g. neurodata.io')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('path', action="store", help='Directory with annotation PNG files.')

  result = parser.parse_args()

  # Get a list of the files in the directories
  for sl in range (startslice,endslice+1,batchsz):

    newdata = np.zeros ( [ batchsz, ytilesz, xtilesz ], dtype=np.uint8 )
   
    for b in range ( batchsz ):

      if ( sl + b <= endslice ):

        # For Daniel's backwards slices
        #slicenum = endslice - startslice - (sl+b)

        # raw data
        filenm = result.path + 'composite_mask_z' + '{:0>4}'.format(sl+b) + '.png'
        print "Opening filenm" + filenm
        import pdb;pdb.set_trace()
        imagedata= imread(filenm)
       # imagedata= Image.open(filenm)
        #imgdata = np.fromfile ( filenm, dtype=np.uint8 )
        testdata= imresize(imagedata, (xtilesz,ytilesz), interp='bilinear', mode=None)


        imgdata= np.asarray(testdata)
        

        testdata= testdata.reshape([ytilesz,xtilesz])
        newdata[b,:,:]  = testdata

        # the last z offset that we ingest, if the batch ends before batchsz
        endz = b


    # Now we have a 1024x1024x16 z-aligned cube.  
    #   Send it to the database.
#    import pdb;pdb.set_trace()
    url = 'http://%s/emca/%s/npdense/%s/%s,%s/%s,%s/%s,%s/' % ( result.baseurl, result.token, _resolution, xoffset, xoffset+xtilesz, yoffset, yoffset+ytilesz, ss+sl, ss+sl+endz+1)

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

